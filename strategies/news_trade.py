import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime, date
import os, time

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
CACHE_FILE = "ff_calendar.xml"
CACHE_TTL = 3600  # 1 hour in seconds

def fetch_calendar():
    """Fetch Forex Factory calendar XML, cached for 1 hour."""
    # Check if cached file exists and is fresh
    if os.path.exists(CACHE_FILE):
        age = time.time() - os.path.getmtime(CACHE_FILE)
        if age < CACHE_TTL:
            with open(CACHE_FILE, "rb") as f:
                return f.read()

    # Otherwise fetch from server
    print("Fetching fresh data from Forex Factory...")
    r = requests.get(URL, timeout=10)
    r.raise_for_status()

    # Save to cache
    with open(CACHE_FILE, "wb") as f:
        f.write(r.content)

    return r.content

def get_today_forexfactory_news():
    xml_data = fetch_calendar()
    root = ET.fromstring(xml_data)

    events = []
    for ev in root.findall("event"):
        def _txt(tag):
            node = ev.find(tag)
            return node.text.strip() if node is not None and node.text else None

        date_str = _txt("date")
        time_str = _txt("time")
        dt_obj = None
        if date_str and time_str and time_str.lower() not in {"all day", "tentative"}:
            try:
                dt_obj = datetime.strptime(f"{date_str} {time_str}", "%m-%d-%Y %I:%M%p")
            except Exception:
                pass

        events.append({
            "datetime": dt_obj,
            "currency": _txt("country"),
            "impact": _txt("impact"),
            "title": _txt("title"),
            "forecast": _txt("forecast"),
            "previous": _txt("previous"),
            "actual": _txt("actual")
        })

    df = pd.DataFrame(events)
    df = df.dropna(subset=["datetime"])

    today_ = date.today()
    df_today = df[
        (df["datetime"].dt.date == today_) &
        (df["impact"].isin(["High", "Medium"]))
    ]

    return df_today.sort_values("datetime").reset_index(drop=True)

# # Example usage
# df_news = get_today_forexfactory_news()
# if df_news.empty:
#     print("No news found for today.")
# else:
#     print(df_news)
