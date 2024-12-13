from flask import Flask, request, jsonify

app = Flask(__name__)

# Route qui accepte une requête POST
@app.route('/api/data', methods=['POST'])
def receive_data():
    try:
        # Récupérer les données JSON de la requête
        data = request.get_json()
        
        # # Vérifier que les données sont valides
        # if not data or 'name' not in data or 'age' not in data:
        #     return jsonify({"error": "Invalid data"}), 400
        
        # # Récupérer les champs
        # name = data['name']
        # age = data['age']
        
        # # Exemple de traitement
        # response = {
        #     "message": f"Hello, {name}! You are {age} years old."
        # }

        print(data)

        response = {
            "message": "Data received successfully."
        }
        
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=8080, debug=True)
