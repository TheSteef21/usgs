"""
USGS Ingestor SADV41 (Flash-lite / Sin dependencias externas)
Para @sismosyterremotos
Parsea feed GeoJSON oficial y mapea a severidad SADV41
"""
import urllib.request
import json
from datetime import datetime

FEEDS = {
    "hour": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",
    "day": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson",
    "week": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson",
}

def severity(mag: float):
    if mag >= 7: return "CRITICO"
    if mag >= 6: return "ALTO"
    if mag >= 5: return "MEDIO"
    return "VIGILANCIA"

def is_panama(lat, lon):
    return 7.0 <= lat <= 9.8 and -83.0 <= lon <= -77.0

def fetch(feed="day"):
    url = FEEDS[feed]
    req = urllib.request.Request(url, headers={'User-Agent': 'SADV41-Telemetry-Hub'})
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode('utf-8'))
    
    events = []
    for f in data["features"]:
        lon, lat, depth = f["geometry"]["coordinates"]
        props = f["properties"]
        ev = {
            "id": f["id"],
            "mag": props["mag"],
            "place": props["place"],
            "time": datetime.fromtimestamp(props["time"]/1000).isoformat(),
            "lat": lat, "lon": lon, "depth": depth,
            "severity": severity(props["mag"] or 0),
            "is_panama": is_panama(lat, lon),
            "url": props["url"],
            "tsunami": props.get("tsunami", 0),
            "alert": props.get("alert"),
        }
        events.append(ev)
    
    events.sort(key=lambda x: x["mag"] or 0, reverse=True)
    return events

if __name__ == "__main__":
    evs = fetch("day")
    print(f"Total: {len(evs)} | Panamá region: {sum(1 for e in evs if e['is_panama'])}")
    for e in evs[:10]:
        flag = "🇵🇦" if e["is_panama"] else "  "
        print(f"{flag} M{e['mag']} {e['severity']} - {e['place']} ({e['lat']},{e['lon']})")
