import requests

page_id = "61595089241972"
access_token = input("Pega tu Access Token: ").strip()

url = f"https://graph.facebook.com/v18.0/{page_id}"
params = {"fields": "instagram_business_account", "access_token": access_token}

response = requests.get(url, params=params)
data = response.json()

if "instagram_business_account" in data:
    ig_user_id = data["instagram_business_account"]["id"]
    print(f"\n¡Éxito! Tu IG_USER_ID es: {ig_user_id}")
    
    with open(".env", "w") as f:
        f.write(f"FB_PAGE_ID={page_id}\n")
        f.write(f"IG_USER_ID={ig_user_id}\n")
        f.write(f"ACCESS_TOKEN={access_token}\n")
    print("Variables guardadas en el archivo .env correctamente.")
else:
    print("\nError: No se encontró cuenta de Instagram Business o el token no tiene permisos.", data)
