import requests
import json


def get_billboard_charts():
    # Variables which hold the alltime Billboard Data and the most recent Billboard Hot 100 Chart
    # This data is updated every Tuesday when the new Billboard drops
    ALLTIME_DATA_URL = "https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main/all.json"
    RECENT_DATA_URL = "https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main/recent.json"

    # Master list which will hold all objects of the Billboard charts
    chart_list = []

    # Try to parse the data from the URL
    try:
        alltime_resp = requests.get(ALLTIME_DATA_URL)
        alltime_resp.raise_for_status()
        alltime_data = alltime_resp.json()

        recent_resp = requests.get(RECENT_DATA_URL)
        recent_resp.raise_for_status()
        recent_data = recent_resp.json()

        if alltime_resp.raise_for_status() and recent_resp.raise_for_status():
            chart_list = alltime_data + [recent_data]
        else:
            print("Error: Could not parse data")
            return 1
    except requests.JSONDecodeError:
        print("Could not parse JSON")
    return chart_list


def get_artist_charts(chart_list, artist):
    if not chart_list:
        print("Error: No Billboard data found")
    else:
        TARGET_ARTIST = artist
        catalog = {}

        # Create a list of every song that the artist has which charted in the top 100
        for chart in chart_list:
            for entry in chart.get("data", []):
                if entry["artist"].lower() == TARGET_ARTIST.lower():
                    song_name = entry["song"]
                    peak = entry["peak_position"]

                    # If the song isn't in the catalog or the current peak position is lower than recorded
                    # Update peak position in catalog
                    if song_name not in catalog or peak < catalog[song_name]:
                        catalog[song_name] = peak

        num_t100 = len(catalog)
        t40_entries = [song for song, peak in catalog.items() if peak <= 40]
        return num_t100, t40_entries


def main():
    artist = input("Which artist do you want a list of?")
    curr_list = get_billboard_charts()
    t100, t40 = get_artist_charts(curr_list, artist)
    print(
        f"{artist} has had {t100} songs in the Billboard Top 100, and the following placed in the top 40: {t40}"
    )
