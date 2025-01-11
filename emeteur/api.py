from flask import Flask, request, jsonify
import redis
import json
import time

# Initialisation de l'application Flask
app = Flask(__name__)

# Connexion à la base de données Redis
redis_client = redis.StrictRedis(host='localhost', port=16379, db=0, decode_responses=True)

# Dictionnaire pour raccourcir les noms de champs
FIELD_MAPPING = {
    'coordonneeX': 'x',
    'coordonneeY': 'y',
    'temperature': 't',
    'portee': 'p',
    'etat': 'e'
}

# Route qui accepte une requête POST
@app.route('/api/capteurs', methods=['POST'])
def receive_data():
    start_time = time.time()  # Début du chronométrage pour mesurer la durée du traitement

    try:
        # Récupérer les données JSON de la requête
        data = request.get_json()
        print("[INFO] Données reçues :", data)  # Affiche les données reçues pour le débogage

        # Valider que les données reçues sont bien une liste JSON
        if not data or not isinstance(data, list):
            print("[ERROR] Les données ne sont pas une liste JSON valide.")  # Avertissement si les données sont invalides
            return jsonify({"error": "Invalid data. Expected a JSON array."}), 400

        # Parcourir chaque objet de la liste pour les stocker ou mettre à jour dans Redis
        for item in data:
            if 'id' not in item:
                # Si l'objet ne contient pas d'ID, retourner une erreur
                print(f"[ERROR] L'élément ne contient pas de champ 'id'. Élément : {item}")  # Log d'erreur
                return jsonify({"error": "Each item must contain an 'id' field."}), 400

            # Reformater l'élément en remplaçant les noms de champs
            formatted_item = {'id': item['id']}  # L'ID reste inchangé
            for key, value in item.items():
                if key != 'id' and key in FIELD_MAPPING:
                    formatted_item[FIELD_MAPPING[key]] = value  # Remplacer le nom du champ

            redis_key = f"capteur:{item['id']}"  # Génération d'une clé unique pour chaque capteur
            print(f"[INFO] Traitement de l'élément avec clé Redis : {redis_key}")  # Affiche la clé en cours de traitement

            # Vérifier si la clé existe déjà dans Redis
            existing_data = redis_client.json().get(redis_key)
            if existing_data:
                print(f"[INFO] Clé existante trouvée. Données existantes : {existing_data}")  # Affiche les données existantes
                if isinstance(existing_data, str):
                    existing_data = json.loads(existing_data)  # Si les données sont une chaîne, les convertir en JSON

                # Mettre à jour uniquement si les nouvelles données diffèrent
                if existing_data != formatted_item:
                    existing_data.update(formatted_item)  # Mise à jour des champs de l'objet
                    redis_client.json().set(redis_key, "$", existing_data)  # Stockage des données mises à jour
                    print(f"[INFO] Données mises à jour pour la clé : {redis_key}")  # Journal de mise à jour
                else:
                    print(f"[INFO] Les données sont identiques. Aucune mise à jour n’a été effectuée pour la clé : {redis_key}")
            else:
                # Si la clé n'existe pas, créer une nouvelle entrée
                redis_client.json().set(redis_key, "$", formatted_item)
                print(f"[INFO] Nouvelles données stockées pour la clé : {redis_key}")  # Journalisation des nouvelles données

        # Calculer le temps total de traitement
        processing_time = time.time() - start_time
        response = {
            "message": f"{len(data)} items processed successfully.",
            "processing_time": f"{processing_time:.2f} seconds"
        }
        print("[INFO]", response)  # Affiche le résumé du traitement
        return jsonify(response), 200

    except Exception as e:
        # En cas d'exception, afficher l'erreur et renvoyer une réponse d'erreur
        print(f"[ERROR] Erreur lors du traitement : {str(e)}")  # Log d'exception
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Lancer l'application Flask sur le port 8080
    app.run(host="0.0.0.0", port=8080, debug=True)
