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
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Eroare la salvare: {e}")

@app.route('/')
def home():
    return "Server is ONLINE on Render!"

# Catch-all: raspunde la absolut orice ruta ceruta de joc
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT'])
def catch_all(path):
    data = request.form.to_dict() if request.form else request.args.to_dict()
    if not data and request.json:
        data = request.json
        
    print(f"\n[CERERE NOUA] Route: /{path} | Metoda: {request.method}")
    print(f"Date primite: {data}")

    level_id = data.get('level_id') or request.args.get('level_id') or 'LevelD70'
    
    # Asiguram un user_id valid pentru joc
    user_id = data.get('user_id') or request.args.get('user_id')
    if not user_id or user_id == '':
        user_id = '10001'

    all_scores = load_data()

    # Daca jocul salveaza un scor
    if 'put' in path or 'save' in path or request.method == 'POST':
        race_time = data.get('time') or data.get('score') or '45000'
        shadow = data.get('shadow', '')
        user_name = data.get('user_name') or data.get('name') or 'Jucator_1'
        
        if level_id not in all_scores:
            all_scores[level_id] = []
        
        entry = {
            "id": user_id,
            "user_id": user_id,
            "username": user_name,
            "name": user_name,
            "time": str(race_time),
            "score": str(race_time),
            "shadow": shadow,
            "bike": str(data.get('bike', '0')),
            "character": str(data.get('character', '0')),
            "rank": 1
        }
        
        # Actualizam scorul existent
        all_scores[level_id] = [s for s in all_scores[level_id] if s.get('user_id') != user_id]
        all_scores[level_id].append(entry)
        save_data(all_scores)
        print(f"--> [SCOR SALVAT CU SUCCES!] Nivel: {level_id} | Timp: {race_time}")
        
        return jsonify({
            "status": True,
            "result": 1,
            "user_id": user_id
        })

    # Daca jocul cere lista de scoruri / world scores
    level_scores = all_scores.get(level_id, [])

    # Daca baza de date e goala, punem un profil demo ca sa se populeze trofeele si garajul
    if not level_scores:
        level_scores = [
            {
                "id": "10001",
                "user_id": "10001",
                "username": "Xtreme_Rider",
                "name": "Xtreme_Rider",
                "time": "41200",
                "score": "41200",
                "bike": "0",
                "character": "0",
                "shadow": "",
                "rank": 1
            }
        ]

    return jsonify({
        "status": True,
        "status_code": 200,
        "result": level_scores,
        "data": level_scores,
        "scores": level_scores,
        "position": 1,
        "user_id": user_id
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
