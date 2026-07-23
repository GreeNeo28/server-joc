from flask import Flask, request, jsonify
import json
import os
import traceback
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "scores_data.json"
ERROR_LOG = "server_errors.log"

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

def log_error(context, exc):
    """Scrie erorile intr-un fisier separat, ca sa le poti vedea si dupa ce
    consola s-a inchis / a scrolat mai departe."""
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"\n[{datetime.now()}] {context}\n")
            f.write(traceback.format_exc())
            f.write("\n")
    except Exception:
        pass
    print(f"[EROARE] {context}: {exc}")

@app.route('/')
def home():
    return "Xtreme Server Pro is Online!"

def get_clean_user_id(val):
    if not val or val == '' or val == 'None':
        return 'local_master_player'
    return str(val)

def get_request_data():
    """Combina TOATE sursele posibile de date (query string, form POST,
    body JSON) intr-un singur dict, fara sa arunce nicio exceptie -
    indiferent ce Content-Type trimite jocul."""
    data = {}
    try:
        data.update(request.args.to_dict())
    except Exception:
        pass
    try:
        if request.form:
            data.update(request.form.to_dict())
    except Exception:
        pass
    try:
        # silent=True inseamna ca NU mai arunca eroare 415 daca Content-Type
        # nu e application/json - pur si simplu ignora si continua
        json_body = request.get_json(silent=True)
        if isinstance(json_body, dict):
            data.update(json_body)
    except Exception:
        pass
    return data

def safe_time_value(raw, default=999999):
    """Transforma orice format de timp trimis de joc (int, float, '01:23.456',
    text cu gunoi in el etc.) intr-un numar intreg sortabil. Nu arunca
    NICIODATA o exceptie - in cel mai rau caz intoarce `default`."""
    if raw is None:
        return default
    s = str(raw).strip()

    try:
        return int(s)
    except (ValueError, TypeError):
        pass

    try:
        return int(float(s))
    except (ValueError, TypeError):
        pass

    if ':' in s:
        try:
            parts = s.split(':')
            total_seconds = 0.0
            for p in parts:
                total_seconds = total_seconds * 60 + float(p)
            return round(total_seconds * 1000)
        except (ValueError, TypeError):
            pass

    digits = ''.join(ch for ch in s if ch.isdigit())
    if digits:
        try:
            return int(digits)
        except ValueError:
            pass

    return default

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

@app.route('/scores/get', methods=['GET', 'POST'])
def get_shadow():
    try:
        data = get_request_data()
        req_id = get_clean_user_id(data.get('id') or data.get('user_id'))

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
    except Exception as e:
        log_error("get_shadow", e)
        return jsonify({"status": True, "result": "", "shadow": ""})

@app.route('/scores/put', methods=['GET', 'POST'])
def put_score():
    try:
        data = get_request_data()

        level_id = data.get('level_id')
        if not level_id:
            print(f"[SALVARE ESUATA] Lipseste level_id. Date primite: {data}")
            return jsonify({"status": False})

        user_id = get_clean_user_id(data.get('user_id'))
        race_time_raw = data.get('time') or data.get('score') or '999999'
        shadow_data = data.get('shadow', '') or ''

        print(f"\n[SALVARE CURSA] Nivel: {level_id} | User: {user_id} | "
              f"Timp brut: {race_time_raw} | Shadow lungime: {len(shadow_data)}")

        entry = {
            "id": user_id,
            "user_id": user_id,
            "name": "Master Player",
            "username": "Master Player",
            "time": str(race_time_raw),
            "score": str(race_time_raw),
            "shadow": shadow_data,
            "bike": str(data.get('bike', '0')),
            "character": str(data.get('character', '0')),
            "rank": 1
        }

        all_scores = load_data()
        if level_id not in all_scores:
            all_scores[level_id] = []

        all_scores[level_id] = [s for s in all_scores[level_id] if s.get('user_id') != user_id]
        all_scores[level_id].append(entry)

        # Sortare care NU mai crapa daca timpul nu e un numar intreg curat
        all_scores[level_id] = sorted(
            all_scores[level_id],
            key=lambda x: safe_time_value(x.get('time'))
        )

        save_data(all_scores)
        print(f"[SALVAT OK] Nivel '{level_id}' are acum {len(all_scores[level_id])} scoruri salvate.")

        return jsonify({"status": True, "result": 1})

    except Exception as e:
        log_error("put_score", e)
        # Raspundem tot cu status True ca jocul sa nu se blocheze/reincerce la
        # infinit - dar eroarea reala ramane scrisa in server_errors.log
        return jsonify({"status": True, "result": 1})

@app.route('/scores/level', methods=['GET', 'POST'])
@app.route('/scores/level_fb', methods=['GET', 'POST'])
def get_scores_level():
    try:
        data = get_request_data()
        level_id = data.get('level_id', '')

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
    except Exception as e:
        log_error("get_scores_level", e)
        return jsonify({"status": True, "result": [], "data": [], "position": 1})

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT'])
def catch_all(path):
    # Util pentru debugging: vezi in consola orice cerere pe care jocul o
    # trimite si pe care serverul inca nu o trateaza explicit.
    print(f"[CATCH-ALL] {request.method} /{path} | args={request.args.to_dict()}")
    return jsonify({"status": True, "result": 1})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
