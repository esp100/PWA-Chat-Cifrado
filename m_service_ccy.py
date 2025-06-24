from flask import Flask, request, jsonify, send_file,  render_template, send_from_directory
from flask_cors import CORS
import requests

app = Flask(__name__, static_folder='static', template_folder='templates')

CORS(app)

CRYPTO_SERVICE_URL = 'http://localhost:5001'
MESSAGE_STORE_SERVICE_URL = 'https://48tc5wxqek.us-east-2.awsapprunner.com'# 'http://localhost:5002'


@app.get('/')
def home():
   return render_template('cli_ccy.html')

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('.', 'manifest.json', mimetype='application/manifest+json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory('.', 'sw.js', mimetype='application/javascript')


@app.route('/send', methods=['POST'])
def send_message():
    data = request.get_json()
    if not data or 'nickname' not in data or 'message' not in data:
        return jsonify({'error': 'Se requiere nickname y mensaje'}), 400

    nickname = data['nickname']
    message = data['message']

    try:
        # Enviar al microservicio de cifrado
        crypto_response = requests.post(f'{CRYPTO_SERVICE_URL}/encrypt', json={'message': f'{nickname}: {message}'})
        crypto_response.raise_for_status()
        encrypted_data = crypto_response.json()
        encrypted_message = encrypted_data.get('encrypted_message')

        if encrypted_message:
            # Enviar al microservicio de almacenamiento
            store_response = requests.post(f'{MESSAGE_STORE_SERVICE_URL}/messages', json={'sender': nickname, 'encrypted_content': encrypted_message})
            store_response.raise_for_status()
            return jsonify({'status': 'Mensaje enviado y almacenado'}), 200
        else:
            return jsonify({'error': 'Error al cifrar el mensaje'}), 500

    except requests.exceptions.ConnectionError as e:
        return jsonify({'error': f'Error de conexión con un microservicio: {e}'}), 500
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': f'Error HTTP al comunicarse con un microservicio: {e}'}), 500

@app.route('/receive', methods=['GET'])
def get_messages():
    try:
        store_response = requests.get(f'{MESSAGE_STORE_SERVICE_URL}/messages')
        store_response.raise_for_status()
        messages = store_response.json()
        return jsonify(messages), 200
    except requests.exceptions.ConnectionError as e:
        return jsonify({'error': f'Error de conexión con el microservicio de almacenamiento: {e}'}), 500
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': f'Error HTTP al obtener mensajes: {e}'}), 500

@app.route('/decrypt', methods=['POST'])
def decrypt_message():
    data = request.get_json()
    if not data or 'encrypted_message' not in data:
        return jsonify({'error': 'Se requiere el mensaje cifrado'}), 400

    encrypted_message = data['encrypted_message']

    try:
        crypto_response = requests.post(f'{CRYPTO_SERVICE_URL}/decrypt', json={'encrypted_message': encrypted_message})
        crypto_response.raise_for_status()
        decrypted_data = crypto_response.json()
        decrypted_message = decrypted_data.get('decrypted_message')

        if decrypted_message is not None:
            return jsonify({'decrypted_message': decrypted_message}), 200
        else:
            return jsonify({'error': 'No se pudo decifrar el mensaje'}), 500

    except requests.exceptions.ConnectionError as e:
        return jsonify({'error': f'Error de conexión con el microservicio de cifrado: {e}'}), 500
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': f'Error HTTP al decifrar el mensaje: {e}'}), 500



if __name__ == '__main__':
    print("Servidor Central (API Gateway) iniciado en el puerto 5000")
    app.run(host='0.0.0.0', port=8000)