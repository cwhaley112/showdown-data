# showdown-data
Simple script to scrape recent battle logs from pokemon showdown. See the API docs here for info on how it works: https://github.com/smogon/pokemon-showdown-client/blob/master/WEB-API.md

# How to use:
1) Clone the repository:
```
git clone https://github.com/cwhaley112/showdown-data.git
```
2) Change settings in `params.py`
3) Collect data:
```
python run.py
```
4) (optional) Schedule this as a background process
This only gets data from 50 battles per minute (I didn't see a way to request a batch of battle logs, and I didn't want to send too many requests). I recommend scheduling this to run in the background on a raspberry pi or an old laptop. The commands I used are:
```
chmod +x run.py # edits file permissions to make this executable by nohup
nohup python3 /path/to/directory/showdown-data/run.py &
```
