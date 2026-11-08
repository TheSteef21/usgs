#!/usr/bin/env python3
import requests
import json

# Cuadrante Extendido: Panamá + Costa Rica + Colombia + Zona de Fractura
MIN_LAT, MAX_LAT = 2.0, 12.0
MIN_LON, MAX_LON = -85.0, -75.0

events = {}

# 1. Obtener datos de USGS (Resumen diario)
try:
    usgs_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    r = requests.get(usgs_url, timeout=10)
    if r.status_code == 200:
        data = r.json()
        for f in data.get('features', []):
            lon, lat, depth = f['geometry']['coordinates']
            if MIN_LAT <= lat <= MAX_LAT and MIN_LON <= lon <= MAX_LON:
                eid = f['id']
                events[eid] = {
                    "id": eid,
                    "mag": f['properties']['mag'],
                    "place": f['properties']['place'],
                    "time": f['properties']['time'],
                    "lat": lat,
                    "lon": lon,
                    "depth": depth,
                    "source": "USGS"
                }
except Exception as e:
    print(f"Error USGS: {e}")

# 2. Obtener datos de EMSC (Captura magnitudes M3.0+ en costas de Azuero/Veraguas)
try:
    emsc_url = f"https://www.seismicportal.eu/fdsnws/event/1/query?format=json&minlat={MIN_LAT}&maxlat={MAX_LAT}&minlon={MIN_LON}&maxlon={MAX_LON}&minmag=3.0"
    r = requests.get(emsc_url, timeout=10)
    if r.status_code == 200:
        data = r.json()
        for f in data.get('features', []):
            props = f['properties']
            geom = f['geometry']
            eid = props.get('unid', f['id'])
            if eid not in events:
                events[eid] = {
                    "id": eid,
                    "mag": props.get('mag'),
                    "place": props.get('flynn_region', 'Panamá Region'),
                    "time": props.get('time'),
                    "lat": geom['coordinates'][1],
                    "lon": geom['coordinates'][0],
                    "depth": geom['coordinates'][2],
                    "source": "EMSC"
                }
except Exception as e:
    print(f"Error EMSC: {e}")

# Guardar sismos consolidados
output_list = list(events.values())
with open("sismos_panama.json", "w") as f:
    json.dump(output_list, f, indent=2)

print(f"✓ Se guardaron {len(output_list)} sismos consolidados (USGS + EMSC) en sismos_panama.json")
