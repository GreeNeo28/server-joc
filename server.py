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
    return "Trial Xtreme 3 Server is UP and Running!"

# 1. AUTENTIFICARE: Cand jocul porneste, cere datele contului. Ii dam un profil valid ca sa deblocheze salvarea!
@app.route('/users/<path:path>', methods=['GET', 'POST'])
def users_handler(path):
    return jsonify({
        "status": True,
        "result": {
            "id": "my_player_1",
            "user_id": "my_player_1",
            "name": "Jucatorul_Meu",
            "username": "Jucatorul_Meu"
        }
    })

# 2. DESCARCARE GHOST: Cand dai Play pe un oponent, jocul cere shadow-ul aici.
@app.route('/scores/get', methods=['GET', 'POST'])
def get_shadow():
    req_id = request.args.get('id')
    if not req_id and request.form:
        req_id = request.form.get('id')
        
    all_scores = load_data()
    found_shadow = ""
    
    # Cautam shadow-ul in baza noastra de date
    for level, scores in all_scores.items():
        for s in scores:
            if str(s.get('id')) == str(req_id) or str(s.get('user_id')) == str(req_id):
                found_shadow = s.get('shadow', '')
                break
        if found_shadow:
            break

    # Jocul asteapta strict string-ul ghost-ului in campul "result"
    return jsonify({
        "status": True,
        "result": found_shadow,
        "shadow": found_shadow
    })

# 3. SALVARE SCOR: Cand treci linia de sosire
@app.route('/scores/put', methods=['GET', 'POST'])
def put_score():
    data = request.form.to_dict() if request.form else request.args.to_dict()
    if not data and request.json:
        data = request.json
        
    level_id = data.get('level_id')
    if not level_id:
        return jsonify({"status": False})
        
    user_id = data.get('user_id', 'my_player_1')
    
    entry = {
        "id": user_id,
        "user_id": user_id,
        "name": data.get('user_name', data.get('name', 'Jucatorul_Meu')),
        "username": data.get('user_name', data.get('name', 'Jucatorul_Meu')),
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
        
    # Stergem scorul vechi al acestui jucator (ca sa pastram doar the best run)
    all_scores[level_id] = [s for s in all_scores[level_id] if s.get('user_id') != user_id]
    all_scores[level_id].append(entry)
    
    # Sortam timpii crescator (timp mic = mai bun)
    all_scores[level_id] = sorted(all_scores[level_id], key=lambda x: int(x.get('time', 999999)))
    
    save_data(all_scores)
    print(f"--> [SUCCES] Am salvat cursa lui {user_id} pe nivelul {level_id}!")
    
    return jsonify({"status": True, "result": 1})

# 4. INCARCARE CLASAMENT: Trimitem oponentii salvati pentru nivelul curent
@app.route('/scores/<path:path>', methods=['GET', 'POST'])
def get_scores(path):
    if path in ['put', 'get']:
        return jsonify({"status": True}) 
        
    level_id = request.args.get('level_id')
    if not level_id and request.form:
        level_id = request.form.get('level_id')
        
    all_scores = load_data()
    level_scores = all_scores.get(level_id, [])
    
    # Recalculam rank-ul bazat pe pozitia in lista sortata
    for index, score in enumerate(level_scores):
        score['rank'] = index + 1
        
    return jsonify({
        "status": True,
        "result": level_scores,
        "position": 1
    })

# CATCH-ALL pt siguranta: Raspundem cu OK la orice alta ruta neprevazuta
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT'])
def catch_all(path):
    return jsonify({"status": True, "result": 1})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
