import threading
import requests
import tkinter as tk
from tkinter import ttk


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

        chart_list = alltime_data
    except requests.exceptions.JSONDecodeError:
        print("Could not parse JSON")
    return chart_list


def get_artist_charts(chart_list, artist):
    if not chart_list:
        print("Error: No Billboard data found")
        return 0, []
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


class BillboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Billboard Chart Lookup")
        self.resizable(False, False)
        self.chart_list = []
        self._build_ui()
        self._start_data_fetch()

    def _build_ui(self):
        outer = tk.Frame(self, padx=16, pady=16)
        outer.pack(fill="both", expand=True)

        tk.Label(
            outer, text="Billboard Chart Lookup", font=("Helvetica", 16, "bold")
        ).pack(anchor="w")

        # Loading indicator
        self.loading_frame = tk.Frame(outer, pady=8)
        self.loading_frame.pack(fill="x")
        tk.Label(self.loading_frame, text="Loading chart data, please wait...").pack(
            side="left"
        )
        self.progress = ttk.Progressbar(
            self.loading_frame, mode="indeterminate", length=180
        )
        self.progress.pack(side="left", padx=(8, 0))
        self.progress.start(10)

        # Search row
        self.search_frame = tk.Frame(outer, pady=8)
        self.search_frame.pack(fill="x")
        tk.Label(self.search_frame, text="Artist:").pack(side="left")
        self.artist_var = tk.StringVar()
        self.entry = tk.Entry(
            self.search_frame, textvariable=self.artist_var, width=32, state="disabled"
        )
        self.entry.pack(side="left", padx=(6, 6))
        self.search_btn = tk.Button(
            self.search_frame, text="Search", command=self._on_search, state="disabled"
        )
        self.search_btn.pack(side="left")

        # Bind Enter key to search
        self.bind("<Return>", lambda _: self._on_search())

        # Results area
        results_frame = tk.Frame(outer, relief="sunken", borderwidth=1)
        results_frame.pack(fill="both", expand=True, pady=(4, 0))

        scrollbar = tk.Scrollbar(results_frame)
        scrollbar.pack(side="right", fill="y")

        self.results_text = tk.Text(
            results_frame,
            yscrollcommand=scrollbar.set,
            wrap="word",
            state="disabled",
            padx=8,
            pady=8,
            width=46,
            height=10,
            relief="flat",
        )
        self.results_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.results_text.yview)

        self._set_results("Enter an artist name above to search.")

    def _set_results(self, text):
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("end", text)
        self.results_text.config(state="disabled")

    def _start_data_fetch(self):
        t = threading.Thread(target=self._fetch_data_thread, daemon=True)
        t.start()

    def _fetch_data_thread(self):
        data = get_billboard_charts()
        # Schedule the UI update back on the main thread
        self.after(0, self._on_data_loaded, data)

    def _on_data_loaded(self, data):
        self.chart_list = data
        self.loading_frame.pack_forget()
        if not data:
            self._set_results(
                "Error: could not load chart data. Check your connection and restart."
            )
            return
        self.entry.config(state="normal")
        self.search_btn.config(state="normal")
        self.entry.focus_set()
        self._set_results("Enter an artist name above to search.")

    def _on_search(self):
        artist = self.artist_var.get().strip()
        if not artist:
            self._set_results("Please enter an artist name.")
            return

        t100, t40 = get_artist_charts(self.chart_list, artist)

        if t100 == 0:
            self._set_results(f'No Billboard Top 100 entries found for "{artist}".')
        elif not t40:
            self._set_results(
                f'"{artist}" has had {t100} song(s) in the Billboard Top 100, '
                f"but none placed in the Top 40."
            )
        else:
            song_list = "\n".join(f"  \u2022 {song}" for song in t40)
            self._set_results(
                f'"{artist}" has had {t100} song(s) in the Billboard Top 100.\n\n'
                f"Top 40 entries ({len(t40)}):\n{song_list}"
            )


if __name__ == "__main__":
    app = BillboardApp()
    app.mainloop()
