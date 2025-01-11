import redis
import json
import paho.mqtt.client as mqtt

# Configuration Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 26379
REDIS_DB = 0
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# Configuration MQTT
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'sensor/data'

def save_to_redis(sensor_data):
    """Enregistre les données formatées dans Redis."""
    try:
        sensor_id = sensor_data.get('id')
        if not sensor_id:
            print("[ERROR] Donnée sans ID, impossible de l'enregistrer.")
            return

        # Utilisation de l'ID comme clé Redis
        key = f"capteur:{sensor_id}"
        redis_client.json().set(key, '$', sensor_data)
        print(f"[INFO] Données enregistrées dans Redis : {key} -> {sensor_data}")
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'enregistrement dans Redis : {e}")

def on_message(client, userdata, msg):
    """Callback exécutée lorsque des données sont reçues depuis MQTT."""
    try:
        payload = msg.payload.decode('utf-8')
        sensor_data = json.loads(payload)
        print(f"[INFO] Données reçues depuis MQTT : {sensor_data}")
        save_to_redis(sensor_data)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Erreur de décodage JSON : {e}")
    except Exception as e:
        print(f"[ERROR] Erreur inattendue : {e}")

def main():
    """Configure et lance le client MQTT."""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message

    try:
        # Connexion au broker MQTT
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        print(f"[INFO] Connecté au broker MQTT à {MQTT_BROKER}:{MQTT_PORT}")

        # Abonnement au topic des capteurs
        client.subscribe(MQTT_TOPIC)
        print(f"[INFO] Abonné au topic : {MQTT_TOPIC}")

        # Boucle pour écouter les messages MQTT
        client.loop_forever()
    except Exception as e:
        print(f"[ERROR] Erreur lors de la connexion ou de l'abonnement MQTT : {e}")

if __name__ == "__main__":
    main()
