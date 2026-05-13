from flask import Flask
import threading
import requests
import mysql.connector
import time
import json

app = Flask(__name__)

# CONFIGURACIÓN - Usa tu IP de GCP
IP_GCP = "34.56.194.241" 

# Estado compartido para mostrar progreso/resultado del hilo de Botón 1
THREAD_STATE = {
    'boton1': {
        'status': 'idle',  # 'idle' | 'running' | 'done' | 'error'
        'result': None,
        'start_time': None
    }
}

@app.route('/')
def index():
    return '''
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Ecosistema Híbrido - Panel de Control</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    background: #f4f7fb;
                    color: #1f2937;
                }
                .container {
                    max-width: 1100px;
                    margin: 0 auto;
                    padding: 40px 20px;
                }
                h1 {
                    text-align: center;
                    margin-bottom: 8px;
                }
                .subtitle {
                    text-align: center;
                    color: #6b7280;
                    margin-bottom: 30px;
                }
                .grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 20px;
                }
                .card {
                    background: white;
                    border-radius: 16px;
                    padding: 22px;
                    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
                    border: 1px solid #e5e7eb;
                }
                .card h2 {
                    margin-top: 0;
                    margin-bottom: 10px;
                }
                .card p {
                    color: #6b7280;
                    line-height: 1.5;
                }
                .actions {
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                    margin-top: 16px;
                }
                button {
                    padding: 12px 16px;
                    border: 0;
                    border-radius: 10px;
                    cursor: pointer;
                    color: white;
                    font-weight: 600;
                }
                .btn-blue { background: #2563eb; }
                .btn-green { background: #16a34a; }
                .result {
                    margin-top: 18px;
                    padding: 16px;
                    background: #f8fafc;
                    border-radius: 12px;
                    min-height: 100px;
                    border: 1px dashed #cbd5e1;
                    overflow-x: auto;
                    max-height: 320px;
                    overflow-y: auto;
                }
                .result pre {
                    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Courier New", monospace;
                    font-size: 12px;
                    background: transparent;
                    margin: 0;
                    white-space: pre-wrap;
                    word-break: break-word;
                }
                .comparison {
                    margin-top: 22px;
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 20px;
                }
                .tag {
                    display: inline-block;
                    padding: 4px 10px;
                    border-radius: 999px;
                    background: #dbeafe;
                    color: #1d4ed8;
                    font-size: 12px;
                    font-weight: 700;
                    margin-bottom: 12px;
                }
            </style>
            <script>
                async function cargarResultado(url, targetId) {
                    const target = document.getElementById(targetId);
                    target.innerHTML = '<em>Cargando...</em>';
                    try {
                        const response = await fetch(url);
                        const html = await response.text();
                        target.innerHTML = html;

                        // Si invocamos boton1, gestionamos estado del botón y arrancamos polling
                        if (url === '/boton1') {
                            const btn = document.getElementById('btn1');
                            // Si la respuesta inicial indica que ya no está corriendo, habilitamos
                            if (html.indexOf('Estado: running') !== -1) {
                                if (btn) btn.disabled = true;
                            } else {
                                if (btn) btn.disabled = false;
                            }

                            const interval = setInterval(async () => {
                                try {
                                    const s = await fetch('/boton1_status');
                                    const text = await s.text();
                                    target.innerHTML = text;
                                    if (text.indexOf('Estado: done') !== -1 || text.indexOf('Estado: error') !== -1) {
                                        clearInterval(interval);
                                        if (btn) btn.disabled = false;
                                    }
                                } catch (e) {
                                    target.innerHTML = '<strong>Error polling:</strong> ' + e.message;
                                    clearInterval(interval);
                                    if (btn) btn.disabled = false;
                                }
                            }, 1000);
                        }
                    } catch (error) {
                        target.innerHTML = '<strong>Error:</strong> ' + error.message;
                    }
                }
            </script>
        </head>
        <body>
            <div class="container">
                <h1>Ecosistema Híbrido - Panel de Control</h1>
                <div class="subtitle">Ambas opciones quedan visibles en la misma pantalla para comparar el comportamiento local y el acceso a la nube.</div>

                <div class="grid">
                    <div class="card">
                        <span class="tag">Concurrencia</span>
                        <h2>Botón 1: Productos de Electrónica</h2>
                        <p>Inicia una tarea en segundo plano con un hilo y consulta una API de productos de electrónica sin bloquear la interfaz.</p>
                        <div class="actions">
                            <button id="btn1" class="btn-blue" onclick="cargarResultado('/boton1', 'resultado1')">Ejecutar Botón 1</button>
                        </div>
                        <div id="resultado1" class="result">Aquí aparecerá el resultado del hilo.</div>
                    </div>

                    <div class="card">
                        <span class="tag">Base de datos</span>
                        <h2>Botón 2: Consulta GCP</h2>
                        <p>Consulta directamente la tabla <strong>inventario</strong> en la base remota y muestra los registros devueltos.</p>
                        <div class="actions">
                            <button class="btn-green" onclick="cargarResultado('/boton2', 'resultado2')">Ejecutar Botón 2</button>
                        </div>
                        <div id="resultado2" class="result">Aquí aparecerán los datos consultados en la nube.</div>
                    </div>
                </div>

                <div class="comparison">
                    <div class="card">
                        <span class="tag">Comparación</span>
                        <h2>¿Qué muestra esta vista?</h2>
                        <p>El panel permite ver en una sola pantalla la respuesta asíncrona del hilo y la respuesta de la base de datos remota, facilitando la comparación entre ambos comportamientos.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
    '''

@app.route('/boton1')
def boton1():
    # REQUISITO: Uso de Concurrencia (Threads)
    def tarea_pesada():
        try:
            print("Iniciando consulta a API de productos de electrónica...")
            resp = requests.get("https://fakestoreapi.com/products/category/electronics", timeout=10)
            productos = resp.json()
            ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            # Formatear productos de forma legible
            resumen = f"[{ts}] Productos de Electrónica (Código: {resp.status_code}):\n"
            for prod in productos[:5]:  # Mostrar los primeros 5 productos
                resumen += f"  • {prod.get('title', 'N/A')}: ${prod.get('price', 'N/A')}\n"
            resumen += f"\nTotal de {len(productos)} productos disponibles."
            THREAD_STATE['boton1']['result'] = resumen
            THREAD_STATE['boton1']['status'] = 'done'
            print("Consulta de productos finalizada.")
        except Exception as e:
            THREAD_STATE['boton1']['status'] = 'error'
            THREAD_STATE['boton1']['result'] = str(e)
            print("Error en consulta de API:", e)
    # Si ya está corriendo, devolvemos el estado actual
    st = THREAD_STATE.get('boton1')
    if st and st.get('status') == 'running':
        return boton1_status()

    # marcamos como running y lanzamos el hilo
    THREAD_STATE['boton1']['status'] = 'running'
    THREAD_STATE['boton1']['start_time'] = time.time()
    THREAD_STATE['boton1']['result'] = None
    hilo = threading.Thread(target=tarea_pesada)
    hilo.start()
    return boton1_status()


@app.route('/boton1_status')
def boton1_status():
    st = THREAD_STATE.get('boton1', {})
    status = st.get('status', 'idle')
    result = st.get('result')
    # Devolvemos HTML simple que el frontend mostrará en el panel
    html = f"<div><strong>Estado:</strong> {status}</div>"
    if status == 'running':
        html += "<div>Ejecutando... espera unos segundos.</div>"
    if result:
        # escapamos un poco para mostrar texto
        safe = str(result).replace('<', '&lt;').replace('>', '&gt;')
        html += f"<div style='margin-top:8px;'><strong>Resultado:</strong><pre style='white-space:pre-wrap'>{safe}</pre></div>"
    return html

@app.route('/boton2')
def boton2():
    try:
        conn = mysql.connector.connect(
            host=IP_GCP, 
            user='santiago_user', 
            password='santiago_password123', 
            database='db_proyecto', 
            port=3306
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM inventario")
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        try:
            pretty = json.dumps(datos, indent=2, default=str, ensure_ascii=False)
        except Exception:
            pretty = str(datos)
        safe = pretty.replace('<', '&lt;').replace('>', '&gt;')
        return f"<h3>☁️ Datos desde GCP:</h3><pre>{safe}</pre>"
    except Exception as e:
        return f"<h3>❌ Error: {e}</h3>"


@app.route('/routes_debug')
def routes_debug():
    # Devuelve la lista de rutas registradas en la app para depuración
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.methods} {rule.rule}")
    return '<br>'.join(routes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)