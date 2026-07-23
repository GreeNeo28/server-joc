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

# Ruta unde jocul trimite scorul si datele ghost-ului
@app.route('/scores/put', methods=['GET', 'POST'])
def report_score():
    data = request.form.to_dict() if request.form else request.args.to_dict()
    if not data and request.json:
        data = request.json

    print(f"[SERVER LOG] Date primite la finalul cursei: {data}")

    level_id = data.get('level_id', 'LevelD80')
    user_id = data.get('user_id', 'player_1')
    user_name = data.get('user_name', 'Jucator')
    race_time = data.get('time', '999999')
    shadow = data.get('shadow', '')

    all_scores = load_data()
    if level_id not in all_scores:
        all_scores[level_id] = []

    entry = {
        "id": user_id,
        "user_id": user_id,
        "username": user_name,
        "name": user_name,
        "time": race_time,
        "score": race_time,
        "shadow": shadow,
        "bike": data.get('bike', '0'),
        "character": data.get('character', '0')
    }

    # Actualizam scorul daca jucatorul exista deja
    existing = [s for s in all_scores[level_id] if s.get('user_id') == user_id]
    if existing:
        existing[0].update(entry)
    else:
        all_scores[level_id].append(entry)

    save_data(all_scores)

    # status: True este obligatoriu pentru Unity!
    return jsonify({
        "status": True,
        "result": 1
    })

# Ruta de unde jocul cere clasamentul si ghost-urile
@app.route('/scores/level', methods=['GET', 'POST'])
@app.route('/scores/level_fb', methods=['GET', 'POST'])
@app.route('/scores/users', methods=['GET', 'POST'])
def get_scores():
    level_id = request.args.get('level_id', '')
    if not level_id and request.form:
        level_id = request.form.get('level_id', '')

    all_scores = load_data()
    level_scores = all_scores.get(level_id, [])

    # status: True deblocheaza afisarea oponentilor in joc!
    return jsonify({
        "status": True,
        "result": level_scores,
        "data": level_scores,
        "position": 1
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
