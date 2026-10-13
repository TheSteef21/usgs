from flask import Flask, request, jsonify, render_template_string
import subprocess

app = Flask(__name__)

# La interfaz HTML, CSS y JavaScript
HTML_PAGE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Termux Web Terminal</title>
    <style>
        body { background-color: #121212; color: #00ff00; font-family: 'Courier New', monospace; padding: 20px; margin: 0; }
        h2 { color: #ffffff; text-align: center; }
        #terminal { 
            background-color: #000; padding: 15px; border: 1px solid #333; 
            border-radius: 5px; height: 60vh; overflow-y: auto; white-space: pre-wrap; 
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
        }
        .input-area { display: flex; margin-top: 15px; }
        .prompt { padding: 10px; background: #222; color: #00ff00; border-radius: 5px 0 0 5px; }
        input { 
            flex-grow: 1; padding: 10px; background: #222; color: #fff; 
            border: none; font-family: 'Courier New', monospace; font-size: 16px; outline: none;
        }
        button { 
            padding: 10px 20px; background: #00ff00; color: #000; border: none; 
            font-weight: bold; cursor: pointer; border-radius: 0 5px 5px 0;
        }
        button:hover { background: #00cc00; }
        .error { color: #ff3333; }
    </style>
</head>
<body>
    <h2>⚡ Consola Web Termux ⚡</h2>
    <div id="terminal"></div>
    <div class="input-area">
        <span class="prompt">~$</span>
        <input type="text" id="cmd" placeholder="Ej. ls -l, pwd, usgs --help" onkeypress="if(event.key === 'Enter') sendCmd()">
        <button onclick="sendCmd()">EJECUTAR</button>
    </div>

    <script>
        async function sendCmd() {
            const input = document.getElementById('cmd');
            const terminal = document.getElementById('terminal');
            const cmd = input.value.trim();
            
            if (!cmd) return;
            
            // Mostrar el comando escrito
            terminal.innerHTML += `<span style="color: #fff;">~$ ${cmd}</span>\\n`;
            input.value = '';

            try {
                const response = await fetch('/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: cmd })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    terminal.innerHTML += `<span class="error">${data.output}</span>\\n\\n`;
                } else {
                    terminal.innerHTML += `${data.output}\\n\\n`;
                }
            } catch (err) {
                terminal.innerHTML += `<span class="error">Error de conexión con el servidor local.</span>\\n\\n`;
            }
            
            // Auto-scroll hacia abajo
            terminal.scrollTop = terminal.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/run', methods=['POST'])
def run_command():
    data = request.get_json()
    cmd = data.get('command', '')
    
    try:
        # Ejecuta el comando en Termux y captura el texto
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        
        # Si hay un error en el comando, devuelve el stderr
        if result.returncode != 0:
            return jsonify({"output": result.stderr.strip() or "Error desconocido", "error": True})
            
        return jsonify({"output": result.stdout.strip(), "error": False})
        
    except Exception as e:
        return jsonify({"output": str(e), "error": True})

if __name__ == '__main__':
    # Se ejecuta solo en localhost (muy importante para la seguridad)
    app.run(host='127.0.0.1', port=5000)

