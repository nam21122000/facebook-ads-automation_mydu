import requests
import os
import json

TOKEN = os.environ["FB_TOKEN"]

CAMPAIGN_ID = "120241647150160573"
NEW_BUDGET = 2000000

GRAPH_URL = f"https://graph.facebook.com/v19.0/{CAMPAIGN_ID}"

def change_budget():

    payload = {
        "daily_budget": NEW_BUDGET,
        "access_token": TOKEN
    }

    print("===== DEBUG START =====")
    print("URL:", GRAPH_URL)
    print("Payload:", json.dumps(payload, indent=2))

    try:

        response = requests.post(GRAPH_URL, data=payload)

        print("Status Code:", response.status_code)

        try:
            data = response.json()
            print("Response JSON:")
            print(json.dumps(data, indent=2))
        except:
            print("Response Text:")
            print(response.text)

    except Exception as e:

        print("Request failed:", str(e))

    print("===== DEBUG END =====")


if __name__ == "__main__":
    change_budget()
