from flask import Flask
import threading
import requests
import mysql.connector

app = Flask(__name__)

# CONFIGURACIÓN - Usa tu IP de GCP
IP_GCP = "34.56.194.241" 

@app.route('/')
def index():
    return '''
        <body style="font-family: Arial; text-align: center; padding-top: 50px;">
            <h1>Ecosistema Híbrido - Panel de Control</h1>
            <hr style="width: 50%;">
            <div style="margin-top: 30px;">
                <button onclick="location.href='/boton1'" style="padding: 15px; background: #2196F3; color: white; border: none; cursor: pointer;">
                    Botón 1: API Externa (Concurrencia)
                </button>
                <button onclick="location.href='/boton2'" style="padding: 15px; background: #4CAF50; color: white; border: none; cursor: pointer; margin-left: 10px;">
                    Botón 2: Consulta Nube (GCP)
                </button>
            </div>
        </body>
    '''

@app.route('/boton1')
def boton1():
    # REQUISITO: Uso de Concurrencia (Threads)
    def tarea_pesada():
        print("Iniciando consulta a API externa...")
        requests.get("https://api.github.com")
        print("Consulta finalizada.")

    hilo = threading.Thread(target=tarea_pesada)
    hilo.start()
    return "<h3>🚀 Hilo iniciado: Consultando API en segundo plano...</h3><a href='/'>Volver</a>"

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
        return f"<h3>☁️ Datos desde GCP:</h3><p>{str(datos)}</p><a href='/'>Volver</a>"
    except Exception as e:
        return f"<h3>❌ Error: {e}</h3><a href='/'>Volver</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)