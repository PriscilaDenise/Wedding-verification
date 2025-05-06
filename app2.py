from flask import Flask, request, render_template_string, jsonify, redirect, url_for
import sqlite3
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SQLite database
def init_db():
    try:
        conn = sqlite3.connect('guests.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS guests (card_number TEXT PRIMARY KEY, guest_code TEXT UNIQUE, scanned INTEGER DEFAULT 0)''')
        
        # Use deterministic guest codes matching guest_list.csv
        sample_guests = [
            (f'{i:03d}', f'G-{chr(65 + (i-1) % 26)}{(i-1) % 10}{chr(65 + ((i-1) // 10) % 26)}', 0)
            for i in range(1, 301)
        ]
        
        c.executemany('INSERT OR IGNORE INTO guests (card_number, guest_code, scanned) VALUES (?, ?, ?)', sample_guests)
        conn.commit()
        logger.info("Database initialized with 300 guest codes.")
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        conn.close()

# Root route
@app.route('/')
def index():
    return redirect(url_for('verify_guest'))

# Catch-all route for any undefined paths
@app.route('/<path:path>')
def catch_all(path):
    return '', 200

# Verification route
@app.route('/gate', methods=['GET', 'POST'])
def verify_guest():
    if request.method == 'POST':
        guest_code = request.form.get('guest_code')
        logger.info(f"Received guest code: {guest_code}")
        if not guest_code:
            logger.error("No guest code provided.")
            return jsonify({'status': 'error', 'message': 'Guest code is required.'})
        
        try:
            conn = sqlite3.connect('guests.db')
            c = conn.cursor()
            c.execute('SELECT card_number, scanned FROM guests WHERE guest_code = ?', (guest_code,))
            guest = c.fetchone()
            
            if not guest:
                conn.close()
                logger.info(f"Invalid guest code: {guest_code}")
                return jsonify({'status': 'error', 'message': 'Invalid guest code.'})
            
            card_number, scanned = guest
            if scanned == 1:
                conn.close()
                logger.info(f"Guest code already used: {guest_code}")
                return jsonify({'status': 'error', 'message': 'This code has already been used.'})
            
            # Mark as scanned
            c.execute('UPDATE guests SET scanned = 1 WHERE guest_code = ?', (guest_code,))
            conn.commit()
            conn.close()
            logger.info(f"Guest code verified: {guest_code}, Card: {card_number}")
            return jsonify({'status': 'success', 'message': f'Welcome! Card Number: {card_number}'})
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return jsonify({'status': 'error', 'message': 'Database error. Please try again.'})
    
    # Enhanced front-end with wedding-themed design
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Wedding Gate Verification</title>
        <link href="[invalid url, do not cite] rel="stylesheet">
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: 'Roboto', sans-serif;
                background: url('[invalid url, do not cite]) no-repeat center center fixed;
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
            console.log("Script loaded");
            const form = document.getElementById('verifyForm');
            if (!form) {
                console.error("Form not found");
            } else {
                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    console.log("Form submitted");
                    const formData = new FormData(form);
                    try {
                        const response = await fetch('/gate', {
                            method: 'POST',
                            body: formData
                        });
                        const result = await response.json();
                        console.log("Response:", result);
                        const resultDiv = document.getElementById('result');
                        resultDiv.style.color = result.status === 'success' ? 'green' : 'red';
                        resultDiv.textContent = result.message;
                    } catch (error) {
                        console.error("Fetch error:", error);
                        const resultDiv = document.getElementById('result');
                        resultDiv.style.color = 'red';
                        resultDiv.textContent = 'Error submitting form. Please try again.';
                    }
                });
            }
        </script>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    try:
        init_db()
        app.run(debug=True, port=5001)
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise