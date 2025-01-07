from flask import Flask, request, jsonify
import redis
import json

# Initialisation de l'application Flask
app = Flask(__name__)

# Connexion à la base de données Redis
redis_client = redis.StrictRedis(host='localhost', port=16379, db=0, decode_responses=True)

# Route qui accepte une requête POST
@app.route('/api/data', methods=['POST'])
def receive_data():
    try:
        # Récupérer les données JSON de la requête
        data = request.get_json()
        print("[INFO] Données reçues :", data)  # Journalisation des données reçues

        # Valider que les données reçues sont bien une liste
        if not data or not isinstance(data, list):
            print("[ERROR] Les données ne sont pas une liste JSON valide.")  # Journalisation d'erreur
            return jsonify({"error": "Invalid data. Expected a JSON array."}), 400

        # Parcourir les objets dans la liste et les stocker dans Redis
        for item in data:
            if 'id' not in item:
                print(f"[ERROR] L'élément ne contient pas de champ 'id'. Élément : {item}")  # Journalisation d'erreur
                return jsonify({"error": "Each item must contain an 'id' field."}), 400

            redis_key = f"capteur:{item['id']}"  # Clé unique pour chaque objet
            print(f"[INFO] Traitement de l'élément avec clé Redis : {redis_key}")  # Journalisation de la clé

            # Vérifier si la clé existe déjà
            existing_data = redis_client.json().get(redis_key)
            if existing_data:
                print(f"[INFO] Clé existante trouvée. Données existantes : {existing_data}")  # Journalisation des données existantes
                # Fusionner les nouvelles données avec les anciennes si besoin
                if isinstance(existing_data, str):
                    existing_data = json.loads(existing_data)  # Désérialiser si string

                # Vérifier si les données sont différentes
                if existing_data != item:
                    existing_data.update(item)  # Mise à jour des données existantes
                    redis_client.json().set(redis_key, "$", existing_data)
                    print(f"[INFO] Données mises à jour pour la clé : {redis_key}")  # Journalisation de la mise à jour
                else:
                    print(f"[INFO] Aucune mise à jour nécessaire pour la clé : {redis_key}")  # Journalisation de l'absence de mise à jour
            else:
                # Stocker les nouvelles données si aucune clé n'existe
                redis_client.json().set(redis_key, "$", item)
                print(f"[INFO] Nouvelles données stockées pour la clé : {redis_key}")  # Journalisation du stockage

        response = {
            "message": f"{len(data)} items processed successfully."
        }
        print("[INFO]", response)  # Journalisation de la réponse
        return jsonify(response), 200
    except Exception as e:
        print(f"[ERROR] Erreur lors du traitement : {str(e)}")  # Journalisation de l'exception
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
