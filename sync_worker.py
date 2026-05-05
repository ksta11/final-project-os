import time
import mysql.connector # Asegúrate de instalarlo o usar un Dockerfile que lo incluya

def sincronizar():
    print("Iniciando job de sincronización cada 10 minutos...")
    # Aquí irá tu lógica para conectar a la IP de GCP y traer los datos
    # Por ahora solo simularemos la conexión
    print("Conectado exitosamente a GCP: [TU_IP_EXTERNA_AQUÍ]")
    print("Sincronización finalizada. Datos guardados en volumen local.")

if __name__ == "__main__":
    while True:
        sincronizar()
        time.sleep(600) # 10 minutos
