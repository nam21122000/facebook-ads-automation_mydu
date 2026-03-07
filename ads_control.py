import requests
import pandas as pd
import os

TOKEN = os.environ["FB_TOKEN"]

sheet_url = "https://docs.google.com/spreadsheets/d/1PuTiNfPhzMnte91dJuYmNAgBcRLxiKQ7sSzBZsZIseg/edit?usp=sharing"

df = pd.read_csv(sheet_url)

for index, row in df.iterrows():

    campaign_id = str(row["Campaign ID"])
    action = str(row["AD"])
    budget = int(row["ADS Max"])

    if action == "Tắt":

        requests.post(
            f"https://graph.facebook.com/v19.0/{campaign_id}",
            data={
                "status": "PAUSED",
                "access_token": TOKEN
            }
        )

    elif action == "Tăng":

        new_budget = int(budget * 1.2)

        requests.post(
            f"https://graph.facebook.com/v19.0/{campaign_id}",
            data={
                "daily_budget": new_budget,
                "access_token": TOKEN
            }
        )

    elif action == "Giảm":

        new_budget = int(budget * 0.8)

        requests.post(
            f"https://graph.facebook.com/v19.0/{campaign_id}",
            data={
                "daily_budget": new_budget,
                "access_token": TOKEN
            }
        )
