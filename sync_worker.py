import mysql.connector
import time
import json
import os

# CONFIGURACIÓN
IP_GCP = "34.56.194.241" 
DB_CONFIG = {
    'host': IP_GCP,
    'user': 'santiago_user',
    'password': 'santiago_password123',
    'database': 'db_proyecto'
}

def job_sincronizacion():
    try:
        print(f"[{time.ctime()}] Conectando a GCP en {IP_GCP}...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Consultar datos de la nube
        cursor.execute("SELECT * FROM inventario")
        datos = cursor.fetchall()
        
        # Guardar en la carpeta de backups (mapeada al volumen)
        if not os.path.exists('backups'):
            os.makedirs('backups')
            
        with open('backups/backup_inventario.json', 'w') as f:
            # Agregamos 'default=str' para que convierta las fechas a texto
            json.dump(datos, f, indent=4, default=str)
        
        print(f"✅ Éxito: {len(datos)} registros replicados localmente.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    while True:
        job_sincronizacion()
        print("Esperando 10 minutos para la siguiente sincronización...")
        time.sleep(600) # 10 minutos como pide la rúbrica