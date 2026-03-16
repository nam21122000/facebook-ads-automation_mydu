import requests
import pandas as pd
import os
import re
import json
import time
import random
import gspread
from google.oauth2.service_account import Credentials

TOKEN = os.environ["FB_TOKEN"]
SHEET_ID = os.environ["SHEET_ID"]
SHEET_NAME = os.environ["SHEET_NAME"]

GRAPH_URL = "https://graph.facebook.com/v19.0/"

creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(creds_json, scopes=scope)
client = gspread.authorize(creds)

sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

data = sheet.get_all_records()
df = pd.DataFrame(data)

headers = sheet.row_values(1)
RESULT_COL = headers.index("Kết quả") + 1

VALID_ACTIONS = {"Tắt", "Tăng ngân sách", "Giảm"}


def parse_budget(value):
    if pd.isna(value):
        return None
    value = re.sub(r"[^\d]", "", str(value))
    return int(value) if value else None


def process_batch(batch, row_map):

    retry_batch = []
    retry_rows = []

    r = requests.post(
        GRAPH_URL,
        data={
            "access_token": TOKEN,
            "batch": json.dumps(batch)
        }
    )

    responses = r.json()

    for i, resp in enumerate(responses):

        row_index = row_map[i]

        if resp["code"] == 200:

            sheet.update_cell(row_index, RESULT_COL, "Thành công")

        else:

            retry_batch.append(batch[i])
            retry_rows.append(row_index)

    return retry_batch, retry_rows


def retry_failed(batch, row_map):

    for attempt in range(4):

        if not batch:
            return

        wait = 2 ** attempt + random.uniform(0, 1)
        print("Retry attempt:", attempt + 1, "waiting", wait)

        time.sleep(wait)

        batch, row_map = process_batch(batch, row_map)

    for row_index in row_map:
        sheet.update_cell(row_index, RESULT_COL, "Lỗi sau retry")


batch = []
row_map = []

for i, row in df.iterrows():

    campaign_id = str(row["Campaign ID"]).strip()
    action = str(row["Điều Chỉnh"]).strip()
    
    result = str(row.get("Kết quả", "")).strip()
    if result == "Thành công":
        continue

    if action not in VALID_ACTIONS:
        continue

    budget = parse_budget(row["Ngân sách"])
    sheet_row = i + 2

    if not campaign_id or campaign_id == "nan":
        continue

    if action == "Tắt":

        batch.append({
            "method": "POST",
            "relative_url": campaign_id,
            "body": "status=PAUSED"
        })

        row_map.append(sheet_row)

    elif action in ["Tăng ngân sách", "Giảm"] and budget:

        batch.append({
            "method": "POST",
            "relative_url": campaign_id,
            "body": f"daily_budget={budget}"
        })

        row_map.append(sheet_row)

    if len(batch) >= 50:

        retry_batch, retry_rows = process_batch(batch, row_map)

        retry_failed(retry_batch, retry_rows)

        batch = []
        row_map = []

        time.sleep(random.uniform(1, 2))


if batch:

    retry_batch, retry_rows = process_batch(batch, row_map)

    retry_failed(retry_batch, retry_rows)
