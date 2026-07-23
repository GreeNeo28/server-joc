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

# Salvarea scorului si a ghost-ului (shadow) la finalul cursei
@app.route('/scores/put', methods=['POST'])
def report_score():
    data = request.form if request.form else request.json or {}
    
    level_id = data.get('level_id', 'default')
    user_id = data.get('user_id', 'player_1')
    user_name = data.get('user_name', 'Jucator')
    race_time = data.get('time', '999999')
    points = data.get('points', '0')
    shadow = data.get('shadow', '')
    bike = data.get('bike', '0')
    character = data.get('character', '0')

    all_scores = load_data()
    if level_id not in all_scores:
        all_scores[level_id] = []

    # Cream obiectul cu datele jucatorului si ghost-ul
    entry = {
        "id": user_id,
        "user_id": user_id,
        "username": user_name,
        "name": user_name,
        "time": race_time,
        "points": points,
        "shadow": shadow,
        "bike": bike,
        "character": character
    }

    # Daca jucatorul exista deja pe acest nivel, ii actualizam timpul
    existing = [s for s in all_scores[level_id] if s.get('user_id') == user_id]
    if existing:
        existing[0].update(entry)
    else:
        all_scores[level_id].append(entry)

    # Sortam timpii (cel mai mic timp primul)
    try:
        all_scores[level_id].sort(key=lambda x: int(x.get('time', 999999)))
    except Exception:
        pass

    save_data(all_scores)
    print(f"[SUCCESS] Scor si Ghost salvat pentru nivelul {level_id} de catre {user_name}")

    return jsonify({"result": 1})

# Returnarea scorurilor si ghost-urilor catre joc
@app.route('/scores/level', methods=['GET'])
@app.route('/scores/level_fb', methods=['GET'])
@app.route('/scores/users', methods=['GET'])
def get_scores():
    level_id = request.args.get('level_id', '')
    all_scores = load_data()
    
    level_scores = all_scores.get(level_id, [])

    return jsonify({
        "result": level_scores,
        "position": 1
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
