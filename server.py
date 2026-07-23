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
    return "Server is ONLINE!"

# Interceptam absolut orice ruta si afisam in loguri tot ce primim (inclusiv POST-uri ascunse)
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT'])
def catch_all(path):
    # Colectam datele indiferent cum sunt trimise (form, args sau json)
    data = request.form.to_dict() if request.form else request.args.to_dict()
    if not data and request.json:
        data = request.json
        
    print(f"\n--- [CERERE] /{path} | Metoda: {request.method} ---")
    print(f"Parametri/Body: {data}")

    # Daca jocul trimite scor sau date prin POST oriunde
    if request.method == 'POST' or 'put' in path or 'save' in path or 'add' in path:
        level_id = data.get('level_id') or request.args.get('level_id')
        race_time = data.get('time') or data.get('score')
        
        if level_id and race_time:
            user_id = data.get('user_id', '10001')
            if not user_id: 
                user_id = '10001'
                
            entry = {
                "id": user_id,
                "user_id": user_id,
                "name": data.get('user_name', data.get('name', 'Xtreme Pro')),
                "username": data.get('user_name', data.get('name', 'Xtreme Pro')),
                "time": str(race_time),
                "score": str(race_time),
                "shadow": data.get('shadow', ''),
                "bike": str(data.get('bike', '0')),
                "character": str(data.get('character', '0')),
                "rank": 1
            }
            
            all_scores = load_data()
            if level_id not in all_scores:
                all_scores[level_id] = []
                
            # Salvam cursa
            all_scores[level_id] = [s for s in all_scores[level_id] if s.get('user_id') != user_id]
            all_scores[level_id].append(entry)
            all_scores[level_id] = sorted(all_scores[level_id], key=lambda x: int(x.get('time', 999999)))
            save_data(all_scores)
            
            print(f"==> [SUCCES] Scor salvat prin POST pe /{path}! Nivel: {level_id} | Timp: {race_time}")
            return jsonify({"status": True, "result": 1, "user_id": user_id})

    # Gestionare rute de utilizatori (combatem user_id gol)
    if 'users' in path:
        return jsonify({
            "status": True,
            "result": {
                "id": "10001",
                "user_id": "10001",
                "name": "Xtreme Pro",
                "username": "Xtreme Pro"
            },
            "user_id": "10001"
        })

    # Gestionare cereri de ghost/shadow
    if 'get' in path:
        req_id = data.get('id') or request.args.get('id', '')
        all_scores = load_data()
        found_shadow = ""
        for level, scores in all_scores.items():
            for s in scores:
                if str(s.get('id')) == str(req_id) or str(s.get('user_id')) == str(req_id):
                    found_shadow = s.get('shadow', '')
                    break
            if found_shadow:
                break
        return jsonify({"status": True, "result": found_shadow, "shadow": found_shadow})

    # Gestionare listare niveluri / scoruri (GET)
    level_id = data.get('level_id') or request.args.get('level_id', '')
    all_scores = load_data()
    level_scores = all_scores.get(level_id, [])
    
    for index, score in enumerate(level_scores):
        score['rank'] = index + 1

    return jsonify({
        "status": True,
        "result": level_scores,
        "data": level_scores,
        "position": 1,
        "user_id": "10001"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
