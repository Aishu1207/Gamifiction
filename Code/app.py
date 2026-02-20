from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import datetime

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('aishu_research.db')
    cursor = conn.cursor()
    # Table for participants
    cursor.execute('''CREATE TABLE IF NOT EXISTS participants 
        (user_id TEXT PRIMARY KEY, name TEXT, age INTEGER, experience TEXT)''')
    # Table for trading logs
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, group_type TEXT, 
         action TEXT, reaction_time_ms INTEGER, timestamp DATETIME)''')
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    conn = sqlite3.connect('aishu_research.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO participants (user_id, name, age, experience) VALUES (?,?,?,?)",
                       (data['user_id'], data['name'], data['age'], data['experience']))
        conn.commit()
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error", "message": "User ID already exists"})
    finally:
        conn.close()

@app.route('/log_data', methods=['POST'])
def log_data():
    data = request.json
    conn = sqlite3.connect('aishu_research.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (user_id, group_type, action, reaction_time_ms, timestamp) VALUES (?,?,?,?,?)",
                   (data['user_id'], data['group_type'], data['action'], data['reaction_time'], datetime.datetime.now()))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    init_db()
    app.run(port=5000, debug=True)
