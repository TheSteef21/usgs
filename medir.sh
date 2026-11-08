#!/usr/bin/env bash
# ==============================================================================
# SADV41 // TSEC MONITOR - medir.sh (Cinturón del Pacífico & 4 Placas)
# ==============================================================================

BASE_DIR="$HOME/sadv41"
STATE_FILE="$BASE_DIR/processed_events.txt"
LOG_FILE="$BASE_DIR/tsec_monitor.log"
USGS_URL="https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

mkdir -p "$BASE_DIR"
touch "$STATE_FILE"

# Coordenadas Globales: Cinturón de Fuego / Cocos-Nazca-Caribe-Panamá
LAT_MIN=-5.0
LAT_MAX=18.0
LON_MIN=-92.0
LON_MAX=-70.0

RESPONSE=$(curl -s --connect-timeout 12 "$USGS_URL")

if [ -z "$RESPONSE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERR: Sin respuesta de USGS Feed" >> "$LOG_FILE"
    exit 1
fi

echo "$RESPONSE" | jq -c '.features[]' | while read -r feature; do
    EVENT_ID=$(echo "$feature" | jq -r '.id')
    MAG=$(echo "$feature" | jq -r '.properties.mag')
    PLACE=$(echo "$feature" | jq -r '.properties.place')
    LON=$(echo "$feature" | jq -r '.geometry.coordinates[0]')
    LAT=$(echo "$feature" | jq -r '.geometry.coordinates[1]')

    # Ignorar eventos procesados
    if grep -q "$EVENT_ID" "$STATE_FILE"; then
        continue
    fi

    # Filtro geográfico en zona amplia
    IN_BOUNDS=$(awk -v lat="$LAT" -v lmin="$LAT_MIN" -v lmax="$LAT_MAX" \
                    -v lon="$LON" -v rmin="$LON_MIN" -v rmax="$LON_MAX" \
        'BEGIN { if (lat >= lmin && lat <= lmax && lon >= rmin && lon <= rmax) print 1; else print 0 }')

    if [ "$IN_BOUNDS" -eq 1 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] SISMO 4-PLACAS: M$MAG - $PLACE" >> "$LOG_FILE"
        echo "$EVENT_ID" >> "$STATE_FILE"
        echo "$feature" > "$BASE_DIR/last_event.json"
        
        # Disparar alerta automática para Instagram
        python3 "$BASE_DIR/instagram_bot.py" "$feature" >> "$LOG_FILE" 2>&1
    fi
done
