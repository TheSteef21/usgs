import http.server
import socketserver
import os
import json
import re

PORT = 5000

# Mapeo de la arquitectura y flujo de trabajo según los archivos de ~/usgs
ARCHITECTURE_MAP = {
    "capas": [
        {
            "id": "adquisicion",
            "titulo": "1. Adquisición y Consultas",
            "color": "#3b82f6",
            "archivos": ["get_ids.py", "api", "usgs"]
        },
        {
            "id": "procesamiento",
            "titulo": "2. Extracción y Procesamiento Landsat",
            "color": "#10b981",
            "archivos": ["extract_landsat.py", "procesar_landsat.py", "sadv41_landsat.py", "landsat_all_in_one.py"]
        },
        {
            "id": "datos",
            "titulo": "3. Telemetría y Almacenamiento",
            "color": "#f59e0b",
            "archivos": ["TSEC_Telemetría.json", "landsat_scene.tar", "landsat_extracted"]
        },
        {
            "id": "servidor",
            "titulo": "4. Servidores y Puntos de Salida",
            "color": "#8b5cf6",
            "archivos": ["app.py", "terminal_web.py", "index.html", "templates"]
        },
        {
            "id": "entorno",
            "titulo": "5. Configuración y Módulos Core",
            "color": "#64748b",
            "archivos": ["sadv41", "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg", "scripts", "tests", "docs", "LICENSE", "README.rst"]
        }
    ],
    "flujos": [
        {"origen": "get_ids.py", "destino": "extract_landsat.py", "label": "IDs de escena"},
        {"origen": "extract_landsat.py", "destino": "landsat_extracted", "label": "Extrae bandas .TIF"},
        {"origen": "landsat_extracted", "destino": "sadv41_landsat.py", "label": "Procesa matrices / RGB / NDWI"},
        {"origen": "sadv41_landsat.py", "destino": "TSEC_Telemetría.json", "label": "Genera Telemetría"},
        {"origen": "TSEC_Telemetría.json", "destino": "app.py", "label": "Consume JSON / API"},
        {"origen": "app.py", "destino": "index.html", "label": "Renderiza Visualización Web"},
        {"origen": "terminal_web.py", "destino": "templates", "label": "Interfaz Web Terminal"}
    ]
}

def scan_directory():
    files_info = []
    for item in sorted(os.listdir('.')):
        if item in ['.git', 'venv', '__pycache__', 'usgs.egg-info']:
            continue
        is_dir = os.path.isdir(item)
        size = 0
        if not is_dir:
            try:
                size = os.path.getsize(item)
            except OSError:
                size = 0
        files_info.append({
            "name": item,
            "type": "folder" if is_dir else "file",
            "size": f"{size / 1024:.1f} KB" if not is_dir else "-"
        })
    return files_info

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            payload = {
                "architecture": ARCHITECTURE_MAP,
                "filesystem": scan_directory()
            }
            self.wfile.write(json.dumps(payload).encode('utf-8'))
            return
        
        # Servir el tablero HTML interactivo
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SADV41 - Dashboard de Arquitectura USGS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: monospace; }
        .glass { background: rgba(22, 27, 34, 0.8); backdrop-filter: blur(8px); border: 1px solid #30363d; }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-7xl mx-auto space-y-6">
        
        <!-- Header -->
        <header class="glass p-6 rounded-xl flex justify-between items-center border-l-4 border-cyan-500">
            <div>
                <h1 class="text-2xl font-bold text-cyan-400">⚡ Mapa de Funcionalidad y Arquitectura USGS</h1>
                <p class="text-xs text-gray-400">Visualización de interconexiones previa a la codificación</p>
            </div>
            <span class="px-3 py-1 bg-cyan-950 text-cyan-400 border border-cyan-800 rounded-full text-xs font-semibold">SADV41 Active</span>
        </header>

        <!-- Diagrama de Flujo Funcional -->
        <section class="glass p-6 rounded-xl space-y-4">
            <h2 class="text-lg font-bold text-emerald-400 flex items-center gap-2">
                <span>🔄</span> Diagrama de Flujo e Interconexiones
            </h2>
            <div id="mermaid-container" class="overflow-x-auto bg-[#161b22] p-4 rounded-lg flex justify-center">
                <div class="mermaid" id="mermaid-graph">
                    <!-- El grafo se genera dinámicamente -->
                </div>
            </div>
        </section>

        <!-- Grilla de Capas de Arquitectura -->
        <div id="layers-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Capas generadas vía JS -->
        </div>

        <!-- Explorador de Archivos Físicos del Directorio -->
        <section class="glass p-6 rounded-xl">
            <h2 class="text-lg font-bold text-amber-400 mb-4">📁 Archivos Detectados en ~/usgs</h2>
            <div id="files-list" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 text-xs">
                <!-- Lista de archivos generada vía JS -->
            </div>
        </section>

    </div>

    <script>
        mermaid.initialize({ startOnLoad: false, theme: 'dark' });

        async function initDashboard() {
            const res = await fetch('/api/data');
            const data = await res.json();
            
            // 1. Renderizar Grafo Mermaid
            let graphDefinition = 'graph TD\\n';
            data.architecture.flujos.forEach(f => {
                const src = f.origen.replace(/[^a-zA-Z0-9]/g, '_');
                const dst = f.destino.replace(/[^a-zA-Z0-9]/g, '_');
                graphDefinition += `    ${src}["${f.origen}"] -->|"${f.label}"| ${dst}["${f.destino}"]\\n`;
            });
            
            const mermaidDiv = document.getElementById('mermaid-graph');
            mermaidDiv.innerHTML = graphDefinition;
            await mermaid.run({ nodes: [mermaidDiv] });

            // 2. Renderizar Capas
            const layersContainer = document.getElementById('layers-grid');
            layersContainer.innerHTML = '';
            data.architecture.capas.forEach(capa => {
                const card = document.createElement('div');
                card.className = 'glass p-5 rounded-xl space-y-3';
                card.style.borderTop = `4px solid ${capa.color}`;
                
                let fileTags = capa.archivos.map(f => 
                    `<span class="px-2 py-1 bg-slate-800 text-gray-300 border border-slate-700 rounded text-xs">${f}</span>`
                ).join(' ');

                card.innerHTML = `
                    <h3 class="font-bold text-sm" style="color: ${capa.color}">${capa.titulo}</h3>
                    <div class="flex flex-wrap gap-1.5 pt-2">${fileTags}</div>
                `;
                layersContainer.appendChild(card);
            });

            // 3. Renderizar Archivos del Sistema
            const filesContainer = document.getElementById('files-list');
            filesContainer.innerHTML = '';
            data.filesystem.forEach(item => {
                const isFolder = item.type === 'folder';
                const icon = isFolder ? '📁' : '📄';
                const textColor = isFolder ? 'text-blue-400 font-semibold' : 'text-gray-300';
                
                filesContainer.innerHTML += `
                    <div class="p-2.5 bg-slate-900/60 rounded border border-slate-800/80 flex justify-between items-center">
                        <span class="${textColor} truncate">${icon} ${item.name}</span>
                        <span class="text-[10px] text-gray-500">${item.size}</span>
                    </div>
                `;
            });
        }

        initDashboard();
    </script>
</body>
</html>"""
        self.wfile.write(html_content.encode('utf-8'))

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f" Servidor de Dashboard listo.")
        print(f" Abre en tu navegador: http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n Servidor detenido.")

