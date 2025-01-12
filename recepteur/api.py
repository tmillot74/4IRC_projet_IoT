from flask import Flask, jsonify
import redis

# Initialisation de l'application Flask
app = Flask(__name__)

# Connexion à la base de données Redis
redis_client = redis.StrictRedis(host='localhost', port=26379, db=0, decode_responses=True)

# Route pour récupérer la dernière entrée de chaque capteur
@app.route('/api/capteurs', methods=['GET'])
def get_latest_entries():
    try:
        # Récupérer tous les flux des capteurs (pattern `capteur:*`)
        streams = redis_client.keys('capteur:*')
        latest_entries = []

        # Parcourir chaque flux pour récupérer la dernière entrée
        for stream in streams:
            # Obtenir la dernière entrée de chaque flux
            last_entry = redis_client.xrevrange(stream, count=1)
            if last_entry:
                entry_id, entry_data = last_entry[0]  # ID et données de l'entrée
                entry_data['stream'] = stream  # Ajouter le nom du stream pour identification
                entry_data['entry_id'] = entry_id  # Ajouter l'ID de l'entrée
                latest_entries.append(entry_data)

        # Si aucune donnée n'est trouvée, renvoyer un message approprié
        if not latest_entries:
            return jsonify({"message": "No sensor data found."}), 404

        # Retourner les données sous forme de réponse JSON
        return jsonify(latest_entries), 200

    except Exception as e:
        # En cas d'exception, afficher l'erreur et renvoyer une réponse d'erreur
        print(f"[ERROR] Erreur lors du traitement : {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Lancer l'application Flask sur le port 8090
    app.run(host="0.0.0.0", port=8090, debug=True)
