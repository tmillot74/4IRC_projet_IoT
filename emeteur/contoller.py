import time
import redis
import json
import serial
import threading

# Configuration de Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 16379
REDIS_DB = 0
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# Configuration du port série
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
ser = serial.Serial()

def init_uart():
    """Initialise la connexion UART."""
    ser.port = SERIAL_PORT
    ser.baudrate = BAUD_RATE
    ser.bytesize = serial.EIGHTBITS
    ser.parity = serial.PARITY_NONE
    ser.stopbits = serial.STOPBITS_ONE
    ser.timeout = None
    ser.xonxoff = False
    ser.rtscts = False
    ser.dsrdtr = False

    print("[INFO] Initialisation du port série...")
    try:
        ser.open()
        print("[INFO] Port série ouvert avec succès.")
    except serial.SerialException as e:
        print(f"[ERROR] Impossible d'ouvrir le port série : {e}")
        exit()

def send_uart_message(message):
    """Envoie un message via le port série."""
    try:
        ser.write(message.encode())
        print(f"[INFO] Message envoyé : {message}")
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'envoi du message : {e}")

def sendWithAck(message):
    """Envoie un message sur le port série et attend un acquittement (ACK)."""
    ackReceived = False
    while not ackReceived:
        ser.write((message + "\r\n").encode())
        print(f"[DEBUG] Message envoyé : {message}")

        response = b''
        while True:
            byte = ser.read(1)
            if byte == b'\n':
                break
            response += byte

        response_decoded = response.decode('utf-8').strip()
        print(f"[DEBUG] Réponse reçue : {response_decoded}")

        if response_decoded == "ACK":
            ackReceived = True
            print("[INFO] Acquittement reçu pour le message.")
        else:
            print("[WARNING] Pas d'acquittement, renvoi du message.")

def fetch_and_send_data():
    """Récupère les données de Redis et les envoie via UART."""
    try:
        start_time = time.time()

        # Récupérer toutes les clés correspondant aux capteurs
        keys = redis_client.keys("capteur:*")
        print(f"[INFO] Clés récupérées : {keys}")

        sensor_data = []
        for key in keys:
            data = redis_client.json().get(key)
            if data:
                print(f"[INFO] Données récupérées pour {key} : {data}")
                sensor_data.append(data)

                if len(sensor_data) == 2:
                    message = json.dumps(sensor_data)
                    sendWithAck(message)
                    sensor_data = []

        if sensor_data:
            message = json.dumps(sensor_data)
            sendWithAck(message)

        print("[INFO] Toutes les données ont été envoyées.")

        elapsed_time = time.time() - start_time
        print(f"[INFO] Temps d'exécution du thread : {elapsed_time:.2f} secondes.")
    except Exception as e:
        print(f"[ERROR] Erreur lors de la récupération ou de l'envoi des données : {e}")

def periodic_thread_runner():
    """Lance le thread périodiquement si la dernière exécution est terminée et que l'intervalle est respecté."""
    last_execution_time = 0
    thread_lock = threading.Lock()

    def run_thread():
        nonlocal last_execution_time
        with thread_lock:
            if time.time() - last_execution_time >= 10:
                print("[INFO] Lancement du thread de récupération et envoi des données.")
                fetch_and_send_data()
                last_execution_time = time.time()

    while True:
        run_thread()
        time.sleep(1)

if __name__ == "__main__":
    init_uart()
    print("[INFO] Démarrage de la tâche périodique...")

    thread = threading.Thread(target=periodic_thread_runner, daemon=True)
    thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[INFO] Arrêt du programme.")
        ser.close()
