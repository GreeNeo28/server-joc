from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = "scores_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    return "Server is LIVE!"

# 1. RUTA CHEIE PENTRU AUTENTIFICARE: Aici reparam problema cu "user_id=" gol!
@app.route('/scores/users', methods=['GET', 'POST'])
def get_users():
    # Indiferent ce cere jocul, ii returnam un profil valid ca sa stie ca existam
    return jsonify({
        "status": True,
        "result": [
            {
                "id": "player_xtreme_007",
                "user_id": "player_xtreme_007",
                "name": "Xtreme Pro",
                "username": "Xtreme Pro",
                "country": "RO"
            }
        ]
    })

# 2. DESCARCARE GHOST
@app.route('/scores/get', methods=['GET', 'POST'])
def get_shadow():
    req_id = request.args.get('id') or request.form.get('id', '')
    all_scores = load_data()
    found_shadow = ""
    
    for level, scores in all_scores.items():
        for s in scores:
            if str(s.get('id')) == str(req_id) or str(s.get('user_id')) == str(req_id):
                found_shadow = s.get('shadow', '')
                break
        if found_shadow:
            break

    return jsonify({
        "status": True,
        "result": found_shadow,
        "shadow": found_shadow
    })

# 3. SALVARE SCOR SI GHOST
@app.route('/scores/put', methods=['GET', 'POST'])
def put_score():
    data = request.form.to_dict() if request.form else request.args.to_dict()
    if not data and request.json:
        data = request.json
        
    print(f"\n[!!! SCOR NOU PRIMIT !!!] Date: {data}")
        
    level_id = data.get('level_id')
    if not level_id:
        return jsonify({"status": False})
        
    # Folosim ID-ul fortat de noi daca jocul tot nu trimite unul
    user_id = data.get('user_id')
    if not user_id or user_id == '':
        user_id = "player_xtreme_007"
    
    entry = {
        "id": user_id,
        "user_id": user_id,
        "name": data.get('user_name', data.get('name', 'Xtreme Pro')),
        "username": data.get('user_name', data.get('name', 'Xtreme Pro')),
        "time": str(data.get('time', data.get('score', '999999'))),
        "score": str(data.get('time', data.get('score', '999999'))),
        "shadow": data.get('shadow', ''),
        "bike": str(data.get('bike', '0')),
        "character": str(data.get('character', '0')),
        "rank": 1
    }
    
    all_scores = load_data()
    if level_id not in all_scores:
        all_scores[level_id] = []
        
    all_scores[level_id] = [s for s in all_scores[level_id] if s.get('user_id') != user_id]
    all_scores[level_id].append(entry)
    all_scores[level_id] = sorted(all_scores[level_id], key=lambda x: int(x.get('time', 999999)))
    
    save_data(all_scores)
    
    return jsonify({"status": True, "result": 1})

# 4. INCARCARE CLASAMENT PE NIVEL
@app.route('/scores/level', methods=['GET', 'POST'])
@app.route('/scores/level_fb', methods=['GET', 'POST'])
def get_scores_level():
    level_id = request.args.get('level_id') or request.form.get('level_id', '')
        
    all_scores = load_data()
    level_scores = all_scores.get(level_id, [])
    
    for index, score in enumerate(level_scores):
        score['rank'] = index + 1
        
    return jsonify({
        "status": True,
        "result": level_scores,
        "position": 1
    })

# CATCH-ALL
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT'])
def catch_all(path):
    print(f"[CATCH-ALL] S-a cerut ruta: /{path}")
    return jsonify({"status": True, "result": 1})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
