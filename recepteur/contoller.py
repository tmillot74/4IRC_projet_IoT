import time
import serial
import json
import paho.mqtt.client as mqtt
from datetime import datetime

# Configuration MQTT
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'sensor/data'

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

def format_and_publish_to_mqtt(raw_data, mqtt_client):
    """Formate les données reçues et les publie sur un topic MQTT."""
    try:
        # Chargement des données JSON
        data_list = json.loads(raw_data)

        for sensor_data in data_list:
            formatted_sensor = {new_key: sensor_data[old_key] for new_key, old_key in FIELD_MAPPING.items() if old_key in sensor_data}
            formatted_sensor['id'] = sensor_data['id']  # Ajout de l'ID sans mapping
            formatted_sensor['timestamp'] = datetime.now().isoformat()  # Ajout du timestamp

            # Publication sur MQTT
            mqtt_client.publish(MQTT_TOPIC, json.dumps(formatted_sensor))
            print(f"[INFO] Données publiées sur MQTT : {formatted_sensor}")
    except json.JSONDecodeError as e:
        print(f"[ERROR] Erreur de décodage JSON : {e}")
    except Exception as e:
        print(f"[ERROR] Erreur lors du formatage ou de la publication des données : {e}")

def read_from_uart(mqtt_client):
    """Lit les données depuis le port série et les publie sur MQTT."""
    try:
        while True:
            # Lecture d'une ligne complète depuis le port série
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"[INFO] Données reçues : {line}")
                format_and_publish_to_mqtt(line, mqtt_client)
    except Exception as e:
        print(f"[ERROR] Erreur lors de la lecture depuis le port série : {e}")

if __name__ == "__main__":
    init_uart()

    # Initialisation du client MQTT
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

    print("[INFO] Lecture des données depuis le Micro:bit et publication sur MQTT...")
    try:
        read_from_uart(mqtt_client)
    except KeyboardInterrupt:
        print("[INFO] Arrêt du programme par l'utilisateur.")
    finally:
        ser.close()
        mqtt_client.disconnect()
        print("[INFO] Port série fermé et déconnexion MQTT.")
