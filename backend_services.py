from flask import Flask, request, jsonify
from flask_cors import CORS
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
import os
import sys
import traceback

app = Flask(__name__)
CORS(app)

# --- Lógica de Crypto --- 
KEY = os.environ.get('CRYPTO_KEY')
IV = os.environ.get('CRYPTO_IV')

if not KEY or not IV:
    raise RuntimeError("Las variables de entorno CRYPTO_KEY y CRYPTO_IV no están definidas.")

KEY = bytes.fromhex(KEY)
IV = bytes.fromhex(IV)



def cypher(message: str) -> str:
    cipher_c = AES.new(KEY, AES.MODE_CFB, IV)
    ciphered_bytes = cipher_c.encrypt(message.encode('utf-8'))
    return b64encode(ciphered_bytes).decode('utf-8')

def decypher(encrypted_message: str) -> str | None:
    cipher_d = AES.new(KEY, AES.MODE_CFB, IV)
    try:
        decoded_bytes = b64decode(encrypted_message)
        decrypted_bytes = cipher_d.decrypt(decoded_bytes)
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"Error al decifrar: {e}")
        return None

@app.route('/encrypt', methods=['POST'])
def encrypt_endpoint():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Se requiere el mensaje'}), 400
    encrypted = cypher(data['message'])
    return jsonify({'encrypted_message': encrypted}), 200

@app.route('/decrypt', methods=['POST'])
def decrypt_endpoint():
    data = request.get_json()
    if not data or 'encrypted_message' not in data:
        return jsonify({'error': 'Se requiere el mensaje cifrado'}), 400
    decrypted = decypher(data['encrypted_message'])
    if decrypted is not None:
        return jsonify({'decrypted_message': decrypted}), 200
    else:
        return jsonify({'error': 'No se pudo decifrar el mensaje'}), 400

# --- Lógica de Storage ---
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
    print("Microservicios de Backend (Crypto y Storage) iniciados en el puerto 8080")
    app.run()