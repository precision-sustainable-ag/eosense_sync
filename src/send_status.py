import json
import requests
import glob
import os
import datetime
import logging

logging.basicConfig(filename='status.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Pull setup from config.json
with open("config.json", "r") as file:
    config = json.load(file)

SLACK_HOOK = config["SLACK_HOOK"]

# node_name = os.path.split(glob.glob("/home/mp*")[0])[-1]
# for testing:
# node_name = os.path.split(glob.glob("/home/p*")[0])[-1]
node_name = os.path.split(os.getcwd())[-1]

msg_body = {"text" : f"Node `{node_name}` is active at `{datetime.datetime.now()} UTC`."}

rq = requests.post(SLACK_HOOK, json = msg_body)

if rq.status_code != 200:
    logging.warning(f"  Slack webhook returned status {rq.status_code} {rq.content}")
