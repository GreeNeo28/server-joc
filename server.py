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
    return "Xtreme Server Pro is Online!"

# Functie ajutatoare care curata si forteaza un ID valid pentru jucator
def get_clean_user_id(val):
    if not val or val == '' or val == 'None':
        return 'local_master_player'
    return str(val)

# 1. RUTA DE UTILIZATOR / PROFIL
@app.route('/scores/users', methods=['GET', 'POST'])
def handle_users():
    return jsonify({
        "status": True,
        "result": {
            "id": "local_master_player",
            "user_id": "local_master_player",
            "name": "Master Player",
            "username": "Master Player"
        },
        "user_id": "local_master_player"
    })

# 2. DESCARCARE GHOST (Cand dai Play pe oponent)
@app.route('/scores/get', methods=['GET', 'POST'])
def get_shadow():
    req_id = request.args.get('id') or request.form.get('id', '')
    req_id = get_clean_user_id(req_id)
    
    all_scores = load_data()
    found_shadow = ""
    
    for level, scores in all_scores.items():
        for s in scores:
            if str(s.get('id')) == req_id or str(s.get('user_id')) == req_id:
                found_shadow = s.get('shadow', '')
                break
        if found_shadow:
            break

    return jsonify({
        "status": True,
        "result": found_shadow,
        "shadow": found_shadow
    })

# 3. SALVARE SCOR SI GHOST (La finalul cursei)
@app.route('/scores/put', methods=['GET', 'POST'])
def put_score():
    data = request.form.to_dict() if request.form else request.args.to_dict()
    if not data and request.json:
        data = request.json
        
    level_id = data.get('level_id') or request.args.get('level_id')
    if not level_id:
        return jsonify({"status": False})
        
    # Fortam ID-ul stabil indiferent ce trimite jocul
    user_id = get_clean_user_id(data.get('user_id') or request.args.get('user_id'))
    
    race_time = data.get('time') or data.get('score') or '999999'
    shadow_data = data.get('shadow', '')
    
    print(f"\n[SALVARE CURSA] Nivel: {level_id} | User: {user_id} | Timp: {race_time} | Shadow lungime: {len(shadow_data)}")
    
    entry = {
        "id": user_id,
        "user_id": user_id,
        "name": "Master Player",
        "username": "Master Player",
        "time": str(race_time),
        "score": str(race_time),
        "shadow": shadow_data,
        "bike": str(data.get('bike', '0')),
        "character": str(data.get('character', '0')),
        "rank": 1
    }
    
    all_scores = load_data()
    if level_id not in all_scores:
        all_scores[level_id] = []
        
    # Eliminam duplicatele anterioare ale aceluiasi jucator pe nivel si adaugam timpul nou
    all_scores[level_id] = [s for s in all_scores[level_id] if s.get('user_id') != user_id]
    all_scores[level_id].append(entry)
    
    # Sortam timpii crescator (cel mai rapid timp primul)
    all_scores[level_id] = sorted(all_scores[level_id], key=lambda x: int(x.get('time', 999999)))
    
    save_data(all_scores)
    
    return jsonify({"status": True, "result": 1})

# 4. INCARCARE CLASAMENT PE NIVEL (Garaj / World Scores)
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
        "data": level_scores,
        "position": 1
    })

# CATCH-ALL PENTRU ORICE ALTA CERERE
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT'])
def catch_all(path):
    return jsonify({"status": True, "result": 1})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
