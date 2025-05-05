from flask import Flask, request, render_template_string, jsonify, redirect, url_for
import sqlite3

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('guests.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS guests 
                 (card_number TEXT PRIMARY KEY, guest_code TEXT UNIQUE, scanned INTEGER DEFAULT 0)''')
    
    # Use deterministic guest codes matching guest_list.csv
    sample_guests = [
        (f'{i:03d}', f'G-{chr(65 + (i-1) % 26)}{(i-1) % 10}{chr(65 + ((i-1) // 10) % 26)}', 0)
        for i in range(1, 301)
    ]
    
    c.executemany('INSERT OR IGNORE INTO guests (card_number, guest_code, scanned) VALUES (?, ?, ?)', sample_guests)
    conn.commit()
    conn.close()

# Root route
@app.route('/')
def index():
    return redirect(url_for('verify_guest'))

# Catch-all route for any undefined paths
@app.route('/<path:path>')
def catch_all(path):
    return '', 200

# Reset scans route (admin access)
@app.route('/reset_scans', methods=['GET', 'POST'])
def reset_scans():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'your_secure_password':  # Replace with a strong password
            conn = sqlite3.connect('guests.db')
            c = conn.cursor()
            c.execute('UPDATE guests SET scanned = 0')
            conn.commit()
            conn.close()
            return jsonify({'status': 'success', 'message': 'All scans reset to 0.'})
        return jsonify({'status': 'error', 'message': 'Invalid password.'})
    
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reset Scans</title>
        <style>
            body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f0f0f0; }
            .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); text-align: center; }
            input { padding: 10px; margin: 10px 0; width: 200px; }
            button { padding: 10px 20px; background: #4B0082; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #6A0DAD; }
            #result { margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Reset All Scans</h2>
            <form id="resetForm">
                <input type="password" name="password" placeholder="Enter Password" required>
                <button type="submit">Reset Scans</button>
            </form>
            <div id="result"></div>
        </div>
        <script>
            document.getElementById('resetForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const response = await fetch('/reset_scans', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                const resultDiv = document.getElementById('result');
                resultDiv.style.color = result.status === 'success' ? 'green' : 'red';
                resultDiv.textContent = result.message;
            });
        </script>
    </body>
    </html>
    ''')

# Verification route
@app.route('/gate', methods=['GET', 'POST'])
def verify_guest():
    if request.method == 'POST':
        guest_code = request.form.get('guest_code')
        conn = sqlite3.connect('guests.db')
        c = conn.cursor()
        c.execute('SELECT card_number, scanned FROM guests WHERE guest_code = ?', (guest_code,))
        guest = c.fetchone()
        
        if not guest:
            conn.close()
            return jsonify({'status': 'error', 'message': 'Invalid guest code.'})
        
        card_number, scanned = guest
        if scanned == 1:
            conn.close()
            return jsonify({'status': 'error', 'message': 'This code has already been used.'})
        
        # Mark as scanned
        c.execute('UPDATE guests SET scanned = 1 WHERE guest_code = ?', (guest_code,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': f'Welcome! Card Number: {card_number}'})
    
    # Enhanced front-end with wedding-themed design
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Wedding Gate Verification</title>
        <link href="https://fonts.googleapis.com/css2?family=Great_Vibes&family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: 'Roboto', sans-serif;
                background: url('https://images.unsplash.com/photo-1519741497674-611481863552?ixlib=rb-4.0.3&auto=format&fit=crop&w=1350&q=80') no-repeat center center fixed;
                background-size: cover;
                color: #333;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
            }
            .container {
                position: relative;
                background: rgba(255, 255, 255, 0.95);
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                max-width: 400px;
                width: 90%;
                text-align: center;
                animation: fadeIn 1s ease-in-out;
            }
            h1 {
                font-family: 'Great Vibes', cursive;
                font-size: 48px;
                color: #4B0082;
                margin-bottom: 20px;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
            }
            p {
                font-size: 16px;
                margin-bottom: 20px;
                color: #555;
            }
            .form-container {
                margin: 20px 0;
            }
            input[type="text"] {
                width: 100%;
                padding: 12px;
                font-size: 16px;
                border: 2px solid #4B0082;
                border-radius: 8px;
                margin-bottom: 15px;
                box-sizing: border-box;
                transition: border-color 0.3s ease;
            }
            input[type="text"]:focus {
                border-color: #6A0DAD;
                outline: none;
            }
            button {
                background: #4B0082;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: background 0.3s ease, transform 0.2s ease;
            }
            button:hover {
                background: #6A0DAD;
                transform: scale(1.05);
            }
            #result {
                margin-top: 20px;
                font-size: 18px;
                font-weight: bold;
                min-height: 24px;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @media (max-width: 500px) {
                h1 { font-size: 36px; }
                .container { padding: 20px; }
            }
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="container">
            <h1>Welcome to Our Wedding</h1>
            <p>Please enter your guest code to verify entry.</p>
            <div class="form-container">
                <form id="verifyForm">
                    <input type="text" name="guest_code" placeholder="Enter Guest Code" required>
                    <button type="submit">Verify</button>
                </form>
                <div id="result"></div>
            </div>
        </div>
        <script>
            document.getElementById('verifyForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const response = await fetch('/gate', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                const resultDiv = document.getElementById('result');
                resultDiv.style.color = result.status === 'success' ? 'green' : 'red';
                resultDiv.textContent = result.message;
            });
        </script>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)