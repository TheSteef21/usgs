import os
import sys
import argparse
import requests
from PIL import Image, ImageDraw

USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

def fetch_usgs_panama(min_magnitude=4.5):
    params = {
        "format": "geojson",
        "starttime": "NOW - 1 day",
        "minmagnitude": min_magnitude,
        "minlatitude": 7.0,
        "maxlatitude": 10.0,
        "minlongitude": -83.0,
        "maxlongitude": -77.0
    }
    try:
        res = requests.get(USGS_URL, params=params, timeout=15)
        res.raise_for_status()
        return res.json().get("features", [])
    except Exception as e:
        print(f"[!] Error consultando API USGS: {e}")
        return []

def generate_sismo_image(sismo_data, output_path="latest.jpg"):
    props = sismo_data.get("properties", {})
    mag = props.get("mag", "N/A")
    place = props.get("place", "Panamá Region")
    
    img = Image.new("RGB", (1080, 1080), color=(18, 18, 18))
    draw = ImageDraw.Draw(img)
    
    draw.text((50, 100), "SADV41 TELEMETRIA SISMICA", fill=(255, 255, 255))
    draw.text((50, 300), f"MAGNITUD: {mag}", fill=(255, 69, 0))
    draw.text((50, 450), f"UBICACION: {place}", fill=(255, 255, 255))
    
    img.save(output_path)
    print(f"[+] Imagen generada: {output_path}")

def publish_meta_graph(image_url, caption):
    ig_user_id = os.getenv("IG_USER_ID")
    access_token = os.getenv("ACCESS_TOKEN")
    
    if not ig_user_id or not access_token:
        print("[!] Secrets no configurados. Se omite envio a Graph API.")
        return

    url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": access_token
    }
    
    try:
        res = requests.post(url, data=payload, timeout=15)
        res_data = res.json()
        creation_id = res_data.get("id")
        
        if creation_id:
            pub_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
            requests.post(pub_url, data={"creation_id": creation_id, "access_token": access_token}, timeout=15)
            print("[+] Publicado exitosamente vía Graph API.")
    except Exception as e:
        print(f"[!] Error enviando a Graph API: {e}")

def main():
    parser = argparse.ArgumentParser(description="SADV41 Sismos Watcher Bot")
    parser.add_argument("--check-panama", action="store_true", help="Consulta API USGS para Panamá")
    parser.add_argument("--min-mag", type=float, default=4.5, help="Magnitud mínima")
    args = parser.parse_args()

    if args.check_panama:
        sismos = fetch_usgs_panama(args.min_mag)
        if sismos:
            latest = sismos[0]
            generate_sismo_image(latest, "latest.jpg")
            img_public_url = os.getenv("IMAGE_PUBLIC_URL", "https://thesteef21.github.io/usgs/latest.jpg")
            mag = latest["properties"]["mag"]
            place = latest["properties"]["place"]
            publish_meta_graph(img_public_url, f"ALERTA SISMICA SADV41 | Mag {mag} - {place}")
        else:
            print("[i] Sin sismos significativos detectados.")

if __name__ == "__main__":
    main()
