import requests
import pandas as pd
import os
import re

TOKEN = os.environ["FB_TOKEN"]
sheet_url = os.environ["SHEET_URL"]

df = pd.read_csv(sheet_url)

def parse_budget(value):
    if pd.isna(value):
        return None
    value = re.sub(r"[^\d]", "", str(value))
    return int(value) if value else None

for index, row in df.iterrows():

    campaign_id = str(row["Campaign ID"]).strip()
    action = str(row["Điều Chỉnh"]).strip()
    budget = parse_budget(row["Ngân sách"])

    if not campaign_id or campaign_id == "nan":
        continue

    print("Processing:", campaign_id, action)

    if action == "Tắt":

        requests.post(
            f"https://graph.facebook.com/v19.0/{campaign_id}",
            data={
                "status": "PAUSED",
                "access_token": TOKEN
            }
        )

    elif action in ["Tăng ngân sách", "Giảm"]:

        if budget:

            requests.post(
                f"https://graph.facebook.com/v19.0/{campaign_id}",
                data={
                    "daily_budget": budget,
                    "access_token": TOKEN
                }
            )
