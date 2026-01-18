from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            popcorn_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            address TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/place_order', methods=['POST'])
def place_order():
    data = request.json
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (name, email, popcorn_type, quantity, address, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['name'], data['email'], data['popcorn_type'], data['quantity'], data['address'], datetime.now().isoformat()))
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return jsonify({'order_id': order_id, 'status': 'Pending'})

@app.route('/check_status', methods=['POST'])
def check_status():
    data = request.json
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM orders WHERE id = ?', (data['order_id'],))
    result = cursor.fetchone()
    conn.close()
    if result:
        return jsonify({'status': result[0]})
    else:
        return jsonify({'error': 'Order not found'}), 404

# Simple admin endpoint to update status (e.g., via POST request or tool like Postman)
@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.json
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (data['status'], data['order_id']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Status updated'})

@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/admin/orders')
def admin_orders():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, popcorn_type, quantity, status, created_at FROM orders ORDER BY id DESC')
    orders = cursor.fetchall()
    conn.close()

    orders_list = []
    for o in orders:
        orders_list.append({
            "id": o[0],
            "name": o[1],
            "popcorn_type": o[2],
            "quantity": o[3],
            "status": o[4],
            "created_at": o[5]
        })

    return jsonify(orders_list)


@app.route('/admin/update_status', methods=['POST'])
def admin_update_status():
    data = request.json
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE orders SET status = ? WHERE id = ?',
        (data['status'], data['order_id'])
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Status updated"})

if __name__ == '__main__':
    app.run(debug=False)