import requests
import json


def get_billboard_charts():
    # Variables which hold the alltime Billboard Data and the most recent Billboard Hot 100 Chart
    # This data is updated every Tuesday when the new Billboard drops
    ALLTIME_DATA_URL = "https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main/all.json"
    RECENT_DATA_URL = "https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main/recent.json"

    # Master list which will hold all objects of the Billboard charts
    master_list = []

    # Try to parse the data from the URL
    try:
        alltime_resp = requests.get(ALLTIME_DATA_URL)
        alltime_resp.raise_for_status()
        alltime_data = alltime_resp.json()

        recent_resp = requests.get(RECENT_DATA_URL)
        recent_resp.raise_for_status()
        recent_data = recent_resp.json()

        if alltime_resp.raise_for_status() and recent_resp.raise_for_status():
            master_list = alltime_data + [recent_data]
        else:
            print("Error: Could not parse data")
            return 1
    except requests.JSONDecodeError:
        print("Could not parse JSON")
    return master_list


def get_artist_charts(master_list):
    if not master_list:
        print("Error: No Billboard data found")
    else:
        pass

