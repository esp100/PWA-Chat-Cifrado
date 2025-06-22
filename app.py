from flask import Flask, render_template, send_file
app = Flask(__name__)

@app.get('/')
def home():
   return render_template('main.html')

@app.route('/manifest.json')
def serve_manifest():
    return send_file('manifest.json', mimetype='application/manifest+json')
@app.route('/sw.js')
def serve_sw():
    return send_file('sw.js', mimetype='application/javascript')

if __name__ == '__main__':
   app.run(host='10.100.75.90', port=5008)