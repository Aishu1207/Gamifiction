from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime
import csv
import os

app = Flask(__name__)
CORS(app)

DB_NAME = "aishu_research.db"
CSV_FILE = "trade_logs.csv"

# ---------------------- Initialize Database ----------------------

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Participants table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            age TEXT,
            experience TEXT
        )
    ''')

    # Trade logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            group_type TEXT,
            trade_no INTEGER,
            qty INTEGER,
            price REAL,
            decision_time_secs REAL,
            risk_level TEXT,
            time_elapsed_secs REAL,
            timestamp DATETIME
        )
    ''')

    conn.commit()
    conn.close()


# ---------------------- CSV Writer ----------------------

def save_to_csv(data):

    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="") as file:

        writer = csv.writer(file)

        # Write header only once
        if not file_exists:
            writer.writerow([
                "user_id",
                "group_type",
                "trade_no",
                "qty",
                "price",
                "decision_time_secs",
                "risk_level",
                "time_elapsed_secs",
                "timestamp"
            ])

        writer.writerow([
            data["user_id"],
            data["group_type"],
            data["trade_no"],
            data["qty"],
            data["price"],
            data["decision_time_secs"],
            data["risk_level"],
            data["time_elapsed_secs"],
            datetime.datetime.now()
        ])


# ---------------------- Routes ----------------------

@app.route('/')
def home():
    return "TradePlay Research Backend Running"


# ---------------------- Register Participant ----------------------

@app.route('/register', methods=['POST'])
def register():

    data = request.json

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO participants (user_id, name, age, experience)
            VALUES (?,?,?,?)
        ''', (
            data["user_id"],
            data["name"],
            data["age"],
            data["experience"]
        ))

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "User registered"
        })

    except sqlite3.IntegrityError:

        return jsonify({
            "status": "error",
            "message": "User ID already exists"
        })

    finally:
        conn.close()


# ---------------------- Log Trade ----------------------

@app.route('/log_trade', methods=['POST'])
def log_trade():

    data = request.json

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO logs (
            user_id,
            group_type,
            trade_no,
            qty,
            price,
            decision_time_secs,
            risk_level,
            time_elapsed_secs,
            timestamp
        )
        VALUES (?,?,?,?,?,?,?,?,?)
    ''', (
        data["user_id"],
        data["group_type"],
        data["trade_no"],
        data["qty"],
        data["price"],
        data["decision_time_secs"],
        data["risk_level"],
        data["time_elapsed_secs"],
        datetime.datetime.now()
    ))

    conn.commit()
    conn.close()

    # Save to CSV also
    save_to_csv(data)

    return jsonify({
        "status": "success",
        "message": "Trade logged"
    })


# ---------------------- Get All Logs ----------------------

@app.route('/get_logs', methods=['GET'])
def get_logs():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM logs")
    rows = cursor.fetchall()

    conn.close()

    logs = []

    for r in rows:

        logs.append({
            "id": r[0],
            "user_id": r[1],
            "group_type": r[2],
            "trade_no": r[3],
            "qty": r[4],
            "price": r[5],
            "decision_time_secs": r[6],
            "risk_level": r[7],
            "time_elapsed_secs": r[8],
            "timestamp": r[9]
        })

    return jsonify(logs)


# ---------------------- Get Participants ----------------------

@app.route('/participants', methods=['GET'])
def get_participants():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM participants")
    rows = cursor.fetchall()

    conn.close()

    users = []

    for r in rows:
        users.append({
            "user_id": r[0],
            "name": r[1],
            "age": r[2],
            "experience": r[3]
        })

    return jsonify(users)


# ---------------------- Run Server ----------------------

if __name__ == "__main__":

    init_db()

    print("TradePlay Backend Running...")
    print("API: http://localhost:5000")

    app.run(debug=True, port=5000)