import requests
import pandas as pd
import os
import re
import json
import time
import random

TOKEN = os.environ["FB_TOKEN"]
SHEET_URL = os.environ["SHEET_URL"]

GRAPH_URL = "https://graph.facebook.com/v19.0/"

df = pd.read_csv(SHEET_URL)


def parse_budget(value):
    if pd.isna(value):
        return None
    value = re.sub(r"[^\d]", "", str(value))
    return int(value) if value else None


def send_batch(batch):

    for attempt in range(5):

        r = requests.post(
            GRAPH_URL,
            data={
                "access_token": TOKEN,
                "batch": json.dumps(batch)
            }
        )

        if r.status_code == 200:
            print("Batch success:", len(batch))
            return r.json()

        print("Retry attempt:", attempt + 1)
        print("Error:", r.text)

        wait = random.uniform(2, 5)
        print("Waiting", wait)
        time.sleep(wait)

    print("Batch failed completely")


batch = []

for index, row in df.iterrows():

    campaign_id = str(row["Campaign ID"]).strip()
    action = str(row["Điều Chỉnh"]).strip()
    budget = parse_budget(row["Ngân sách"])

    if not campaign_id or campaign_id == "nan":
        continue

    print("Processing:", campaign_id, action)

    if action == "Tắt":

        batch.append({
            "method": "POST",
            "relative_url": campaign_id,
            "body": "status=PAUSED"
        })

    elif action in ["Tăng ngân sách", "Giảm"] and budget:

        batch.append({
            "method": "POST",
            "relative_url": campaign_id,
            "body": f"daily_budget={budget}"
        })

    else:
        print("Skip:", campaign_id)

    # gửi khi đủ 50
    if len(batch) >= 50:

        send_batch(batch)

        batch = []

        time.sleep(random.uniform(1, 2))


# gửi batch còn lại
if batch:
    send_batch(batch)
