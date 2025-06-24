from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

messages = []

@app.route('/messages', methods=['POST'])
def add_message():
    data = request.get_json()
    if not data or 'sender' not in data or 'encrypted_content' not in data:
        return jsonify({'error': 'Se requiere sender y encrypted_content'}), 400
    messages.append({'sender': data['sender'], 'encrypted_content': data['encrypted_content']})
    return jsonify({'status': 'Mensaje almacenado'}), 201

@app.route('/messages', methods=['GET'])
def get_all_messages():
    return jsonify(messages), 200

if __name__ == '__main__':
    print("Microservicio de Almacenamiento de Mensajes iniciado en el puerto 5002")
    app.run(host='0.0.0.0', port=8000)
