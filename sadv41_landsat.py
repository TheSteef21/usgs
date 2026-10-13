import requests
import sys

# Endpoints y configuración para evadir el WAF
M2M_URL = "https://m2m.cr.usgs.gov/api/api/json/stable/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json"
}

# Credenciales y datos del objetivo
USERNAME = "TheSteef21"
APP_TOKEN = "9jeeBW1Yl4pvtm_@aASRAboDV!Aa1ddFTlB8ItNbW96ynwEghsyke5JJzsSQYvht"
DATASET = "landsat_ot_c2_l1"
SCENE_ID = "LC90120542026278LGN00"

def m2m_request(endpoint, api_key=None, payload=None):
    """Maneja todas las peticiones a la API M2M inyectando el token y las cabeceras."""
    headers = HEADERS.copy()
    if api_key:
        headers["X-Auth-Token"] = api_key

    url = f"{M2M_URL}{endpoint}"
    response = requests.post(url, json=payload or {}, headers=headers)
    
    # Manejo de errores HTTP
    response.raise_for_status()
    data = response.json()
    
    # Manejo de errores internos de la API del USGS
    if data.get("errorCode"):
        print(f"Error USGS [{data['errorCode']}]: {data['errorMessage']}")
        sys.exit(1)
        
    return data.get("data")

def main():
    print("Iniciando telemetría con USGS M2M...")

    # 1. Iniciar sesión y obtener el token temporal
    api_key = m2m_request("login-token", payload={"username": USERNAME, "token": APP_TOKEN})
    print("✓ Autenticación exitosa. API Key generada.")

    # 2. Consultar las opciones de descarga de la escena
    print(f"Consultando opciones para la escena {SCENE_ID}...")
    options_payload = {
        "datasetName": DATASET,
        "entityIds": [SCENE_ID]
    }
    options = m2m_request("download-options", api_key, payload=options_payload)

    if not options:
        print("No se encontraron opciones. Verifica el SCENE_ID.")
        return

    # Extraer el ID del producto descargable (generalmente el bundle completo)
    downloads = []
    for option in options:
        if option.get("available"):
            downloads.append({
                "entityId": option["entityId"],
                "productId": option["id"]
            })

    if not downloads:
        print("La escena existe pero el producto no está disponible para descarga directa.")
        return

    # 3. Solicitar la preparación del enlace de descarga
    print("Solicitando autorización de URL de descarga...")
    download_req_payload = {
        "downloads": downloads,
        "label": "SADV41_Hub_Extraction"
    }
    req_results = m2m_request("download-request", api_key, payload=download_req_payload)

    # 4. Mostrar las URLs obtenidas
    print("\n=== ENLACES DE DESCARGA ===")
    for item in req_results.get("availableDownloads", []):
        print(f"-> {item['url']}")

    # 5. Cerrar sesión para invalidar el token por seguridad
    m2m_request("logout", api_key)
    print("\n✓ Sesión cerrada de forma segura.")

if __name__ == "__main__":
    main()
