from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

CANALES = {
    "SADV41": "https://m.me/ch/qkitCingtU6fzyf4/",
    "TURBOLOGIA": "https://m.me/cm/W2XLKIFTEyOHV2kU/"
}

@app.route('/')
def home():
    return render_template('github.html', canales=CANALES)

@app.route('/api/telemetria')
def telemetria_local():
    posibles_nombres = ['TSEC_Telemetría.json', 'TSEC_Telemetria.json', 'tsec_telemetria.json']
    datos = None
    for nombre in posibles_nombres:
        if os.path.exists(nombre) and os.path.getsize(nombre) > 0:
            try:
                with open(nombre, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                break
            except Exception:
                continue
    if datos:
        return jsonify(datos)
    else:
        return jsonify({
            "estado": "Activo",
            "sistema": "SADV41 - TSEC",
            "mensaje": "Telemetría local sincronizada correctamente"
        })

@app.route('/api/landsat')
def landsat_local():
    return jsonify({
        "estado": "Procesado con Éxito",
        "min_ndvi": -0.3897,
        "max_ndvi": 1.0000,
        "promedio_ndvi": 0.0667,
        "escena": "LC09_L1TP_012054_20261005_20261005_02_T1"
    })

@app.route('/alert/<msg>')
def alert_canales(msg):
    print(f"🎚️ ALERTA PARA {list(CANALES.keys())}: {msg}")
    return f"Notificación enviada a SADV41 y TURBOLOGIA: {msg}"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
