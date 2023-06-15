import json
import logging
import os
import time

import requests

import params

if not (os.path.exists(params.SAVE_DIR) and os.path.isdir(params.SAVE_DIR)):
    os.mkdir(params.SAVE_DIR)


URL_SEARCH = f"https://replay.pokemonshowdown.com/search.json?format={params.FORMAT}"

# replay ID goes between these in the URL
# just getting log from json because the json doesn't offer much additional information and it cuts file size by about 1/3
URL_LOG1 = f"https://replay.pokemonshowdown.com/{params.FORMAT}-"
URL_LOG2 = f".json"

logging.basicConfig(
    filename=params.LOG_FILENAME,
    filemode="a",
    format="%(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,  # set to logging.DEBUG if you're a masochist
)
logger = logging.getLogger("Pokemon Showdown")


def main():
    ids_seen = set()
    ids_seen_old = set()  # will forget ids after 50 pages

    current_batch = dict()
    page = 0

    while True:
        logger.debug(f"Requesting data from page {page}")

        recent_battles = requests.get(f"{URL_SEARCH}&page={page}")
        last_batch_time = time.time()

        if recent_battles.status_code != 200:
            logger.error(
                f"Received http status code {recent_battles.status_code} for batch request"
            )
            time.sleep(1)
            continue

        # recent_battles is list of dictionaries. each dict contains info for a single battle
        recent_battles = recent_battles.json()
        next_page_exists = len(recent_battles) == 51

        num_skipped = 0
        for i in range(len(recent_battles)):
            battle_id = recent_battles[i]["id"].split("-")[
                1
            ]  # full id is '{format}-{id_no}'

            if battle_id in ids_seen or battle_id in ids_seen_old:
                logger.info(f"skipping seen battle_id {battle_id}")
                num_skipped += 1
                continue
            else:
                ids_seen.add(battle_id)

            battle_data = requests.get(f"{URL_LOG1}{battle_id}{URL_LOG2}")

            if battle_data.status_code != 200:
                logger.error(
                    f"Received http status code {battle_data.status_code} for battle_id {battle_id}"
                )
                time.sleep(1)
                continue

            battle_data = battle_data.json()

            current_batch[battle_id] = battle_data["log"]

            if params.DEBUG:
                break

        if params.DEBUG:
            write_data(current_batch)
            break

        if len(current_batch) >= params.BATCH_SIZE:
            logger.info(f"saving {len(current_batch)} battles to disk")
            write_data(current_batch)
            current_batch = dict()

        logger.debug("Got data for batch. Waiting until it's been 1 minute...")
        while time.time() - last_batch_time < 60 and num_skipped / 50 < 0.5:
            time.sleep(1)

        page += 1
        if page > 25 or not next_page_exists:
            page = 0
            ids_seen_old = ids_seen
            ids_seen = set()


def write_data(current_batch):
    path = os.path.join(params.SAVE_DIR, f"{params.FORMAT}-{time.time()}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(current_batch, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
