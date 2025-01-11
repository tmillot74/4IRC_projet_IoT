import time
import redis
import serial
import threading
from datetime import datetime, timedelta
import json

# Configuration de Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 26379
REDIS_DB = 0
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# Configuration du port série
SERIAL_PORT = "/dev/ttyACM1"
BAUD_RATE = 115200
ser = serial.Serial()

# Mapping des champs
FIELD_MAPPING = {
    'coordonneeX': 'x',
    'coordonneeY': 'y',
    'temperature': 't',
    'portee': 'p',
    'etat': 'e'
}

def init_uart():
    """Initialise la connexion UART."""
    ser.port = SERIAL_PORT
    ser.baudrate = BAUD_RATE
    ser.bytesize = serial.EIGHTBITS  # Nombre de bits par octet
    ser.parity = serial.PARITY_NONE  # Pas de parité
    ser.stopbits = serial.STOPBITS_ONE  # 1 bit de stop
    ser.timeout = None  # Lecture bloquante
    ser.xonxoff = False  # Pas de contrôle de flux logiciel
    ser.rtscts = False  # Pas de contrôle de flux matériel RTS/CTS
    ser.dsrdtr = False  # Pas de contrôle de flux matériel DSR/DTR

    print("[INFO] Initialisation du port série...")
    try:
        ser.open()
        print("[INFO] Port série ouvert avec succès.")
    except serial.SerialException as e:
        print(f"[ERROR] Impossible d'ouvrir le port série : {e}")
        exit()

def format_and_save_to_redis(raw_data):
    """Formate les données reçues et les enregistre dans Redis au format JSON."""
    try:
        # Chargement des données JSON
        data_list = json.loads(raw_data)

        for sensor_data in data_list:
            formatted_sensor = {new_key: sensor_data[old_key] for new_key, old_key in FIELD_MAPPING.items() if old_key in sensor_data}
            formatted_sensor['id'] = sensor_data['id']  # Ajout de l'ID sans mapping

            # Ajout dans Redis au format JSON
            timestamp = datetime.now().isoformat()
            key = f"capteur:{formatted_sensor['id']}"
            redis_client.json().set(key, '$', formatted_sensor)

            print(f"[INFO] Données formatées et ajoutées à Redis : {key} -> {formatted_sensor}")
    except json.JSONDecodeError as e:
        print(f"[ERROR] Erreur de décodage JSON : {e}")
    except Exception as e:
        print(f"[ERROR] Erreur lors du formatage ou de l'ajout des données à Redis : {e}")

def read_from_uart():
    """Lit les données depuis le port série, les formate et les stocke dans Redis."""
    try:
        while True:
            # Lecture d'une ligne complète depuis le port série
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"[INFO] Données reçues : {line}")
                format_and_save_to_redis(line)
    except Exception as e:
        print(f"[ERROR] Erreur lors de la lecture depuis le port série : {e}")

if __name__ == "__main__":
    init_uart()
    print("[INFO] Lecture des données depuis le Micro:bit...")
    try:
        read_from_uart()
    except KeyboardInterrupt:
        print("[INFO] Arrêt du programme par l'utilisateur.")
    finally:
        ser.close()
        print("[INFO] Port série fermé.")
