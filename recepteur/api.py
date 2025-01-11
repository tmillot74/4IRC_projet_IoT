from flask import Flask, request, jsonify
import redis
import json
import time

# Initialisation de l'application Flask
app = Flask(__name__)

# Connexion à la base de données Redis
redis_client = redis.StrictRedis(host='10.42.228.117', port=26379, db=0, decode_responses=True)

# Route qui accepte une requête GET pour récupérer tous les capteurs
@app.route('/api/capteurs', methods=['GET'])
def get_all_sensors():
    try:
        # Récupérer toutes les clés de capteurs dans Redis
        keys = redis_client.keys('capteur:*')
        sensors = []

        # Récupérer les données pour chaque capteur
        for key in keys:
            sensor_data = redis_client.json().get(key)
            if sensor_data:
                sensors.append(sensor_data)

        # Si aucun capteur n'est trouvé, renvoyer un message approprié
        if not sensors:
            return jsonify({"message": "No sensors found."}), 404

        # Retourner les capteurs sous forme de réponse JSON
        return jsonify(sensors), 200

    except Exception as e:
        # En cas d'exception, afficher l'erreur et renvoyer une réponse d'erreur
        print(f"[ERROR] Erreur lors du traitement : {str(e)}")  # Log d'exception
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Lancer l'application Flask sur le port 8080
    app.run(host="0.0.0.0", port=8090, debug=True)
