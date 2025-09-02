import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime, date

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"

def get_today_forexfactory_news():
    r = requests.get(URL, timeout=10)
    r.raise_for_status()
    root = ET.fromstring(r.content)

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

        #print("datetime : ", dt_obj.time())

    df = pd.DataFrame(events)

    # Filter only today's events
    today_ = date.today()

    df_today = df[
        (df["datetime"].dt.date == today_) &
        (df["impact"].isin(["High", "Medium"]))
    ]


    return df_today.reset_index(drop=True)

# # Example usage
# df_news = get_today_forexfactory_news()
# if df_news.empty:
#     print("No news found for today.")
# else:
#     print(df_news)
