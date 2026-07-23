from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is ONLINE on Render!"

# Ruta pentru clasamentul general pe nivel
@app.route('/scores/level', methods=['GET'])
def get_scores_level():
    return jsonify({
        "result": [],
        "position": 1
    })

# Ruta pentru scorurile prietenilor / din apropiere
@app.route('/scores/level_fb', methods=['GET'])
def get_scores_level_fb():
    return jsonify({
        "result": [],
        "position": 1
    })

# Ruta pentru profilul / scorul utilizatorilor
@app.route('/scores/users', methods=['GET'])
def get_scores_users():
    return jsonify({
        "result": [],
        "position": 1
    })

# Ruta unde jocul salveaza timpul/scorul la finalul cursei
@app.route('/scores/put', methods=['POST'])
def report_score():
    return jsonify({
        "result": 1
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
