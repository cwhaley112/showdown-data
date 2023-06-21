import json
import logging
import os
import time

import requests

import params

if not (os.path.exists(params.SAVE_DIR) and os.path.isdir(params.SAVE_DIR)):
    os.mkdir(params.SAVE_DIR)

logging.basicConfig(
    filename=params.LOG_FILENAME,
    filemode="a",
    format="%(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,  # set to logging.DEBUG if you're a masochist
)
logger = logging.getLogger("Pokemon Showdown")


def main():
    ids_seen = {format_: set() for format_ in params.FORMATS}
    ids_seen_old = {format_: set() for format_ in params.FORMATS}

    current_batch = {format_: {} for format_ in params.FORMATS}
    page = -1
    format_ix = 0
    next_page_exists = True
    should_cycle_ids = False

    while True:
        page += 1
        if page > 25 or not next_page_exists:
            page = 0
            format_ix = (format_ix + 1) % len(params.FORMATS)

            if should_cycle_ids and format_ix == 0:
                # reset ID trackers
                ids_seen_old = ids_seen
                ids_seen = {format_: set() for format_ in params.FORMATS}
                should_cycle_ids = False

        format_ = params.FORMATS[format_ix]

        logger.info(
            "Battles in memory: "
            + sum([len(current_batch[format_]) for format_ in params.FORMATS])
        )

        # recent_battles is list of dictionaries. each dict contains info for a single battle
        recent_battles = try_request_json(get_replay_url(format_, page))
        if recent_battles is None:
            time.sleep(1)
            continue

        last_batch_time = time.time()
        next_page_exists = len(recent_battles) == 51

        # loop through battles
        num_skipped = 0
        for i in range(len(recent_battles)):
            # full id is '{format}-{id_no}' (or 'smogtours-{format}-{id_no}' if it's a tournament battle)
            battle_id = recent_battles[i]["id"].split("-")[-1]

            if (
                battle_id in ids_seen[format_]
                or battle_id in ids_seen_old[format_]
                or battle_id in current_batch[format_]
            ):
                logger.debug(f"skipping seen battle_id {battle_id}")
                num_skipped += 1
                continue
            else:
                ids_seen[format_].add(battle_id)

            battle_data = try_request_json(get_battle_url(format_, battle_id))
            if battle_data is None:
                time.sleep(1)
                continue

            current_batch[format_][battle_id] = battle_data["log"]

            if params.DEBUG:
                break

        if params.DEBUG:
            write_data(current_batch)
            break

        num_battles = sum([len(current_batch[format_]) for format_ in params.FORMATS])
        if num_battles >= params.BATCH_SIZE:
            logger.info(f"saving {num_battles} battles to disk")
            write_data(current_batch)
            current_batch = {format_: {} for format_ in params.FORMATS}
            should_cycle_ids = True

        logger.debug("Got data for batch. Waiting until it's been 1 minute...")
        logger.info("")
        while time.time() - last_batch_time < 60 and num_skipped / 50 < 0.5:
            time.sleep(1)


def write_data(current_batch):
    path = os.path.join(params.SAVE_DIR, f"battles-{time.time()}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(current_batch, f, ensure_ascii=False)


def try_request_json(url):
    """
    makes GET request for url and returns python dictionary with JSON data

    returns None if we get a bad response or can't decode JSON data
    """

    result = None

    # log request
    logger.info(f"Requesting data from {url}")

    # make request
    try:
        result = requests.get(url)
    except Exception as e:
        logger.error(f"Received exception during `requests.get()`: {e}")

    # check for errors
    if result is None:
        logger.error(f"Received null response for {url}")
    elif result.status_code != 200:
        logger.error(f"Received http status code {result.status_code} for {url}")
        result = None

    if result is not None:
        # try to convert to JSON
        try:
            result = result.json()
        except json.JSONDecodeError:
            logger.error(f"Could not parse request as JSON for {url}")
            result = None

    return result


def get_replay_url(format, pageno):
    return (
        f"https://replay.pokemonshowdown.com/search.json?format={format}&page={pageno}"
    )


def get_battle_url(format, battle_id):
    return f"https://replay.pokemonshowdown.com/{format}-{battle_id}.json"


if __name__ == "__main__":
    main()
