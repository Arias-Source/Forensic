from flask import Flask, render_template_string, request, redirect, url_for, session, flash, send_file, jsonify
from functools import wraps
import os
import time
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from werkzeug.security import check_password_hash
import base64

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store connected users
connected_users = {}

# AES key for encryption (must be 32 bytes for AES-256)
AES_KEY = secrets.token_bytes(32)

# Encrypt password using AES-256
def encrypt_password(password: str) -> str:
    # Create a random 16-byte IV
    iv = secrets.token_bytes(16)
    
    # Pad the password to ensure it's a multiple of block size (128 bits)
    padder = padding.PKCS7(128).padder()
    padded_password = padder.update(password.encode()) + padder.finalize()

    # Encrypt the padded password
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_password = encryptor.update(padded_password) + encryptor.finalize()
    
    # Return the IV + encrypted password (base64 encoded)
    return base64.b64encode(iv + encrypted_password).decode()

# Decrypt AES-256 encrypted password
def decrypt_password(encrypted_password: str) -> str:
    encrypted_data = base64.b64decode(encrypted_password)
    iv = encrypted_data[:16]  # First 16 bytes are the IV
    encrypted_password = encrypted_data[16:]  # The rest is the encrypted password

    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_password = decryptor.update(encrypted_password) + decryptor.finalize()

    # Unpad the password
    unpadder = padding.PKCS7(128).unpadder()
    password = unpadder.update(padded_password) + unpadder.finalize()

    return password.decode()

# User credentials (store encrypted password)
USER_CREDENTIALS = {
    'admin': encrypt_password('admin123')
}

# HTML Template
html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Manager & Sharing</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #2c2f38; color: #fff; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: auto; background-color: #333; padding: 20px; border-radius: 8px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.4); }
        h1 { text-align: center; }
        .file-upload { display: flex; justify-content: center; margin-top: 20px; }
        .file-list { margin-top: 20px; }
        .file { padding: 10px; margin-bottom: 10px; background: #444; border-radius: 5px; cursor: pointer; }
        .file:hover { background: #555; }
        .btn { padding: 8px 15px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .btn:hover { background-color: #45a049; }
        .user-list { margin-top: 20px; padding: 10px; background: #555; border-radius: 5px; }
        .user-list div { margin-bottom: 10px; }
        .alert { padding: 10px; background-color: #f44336; color: white; border-radius: 5px; margin-top: 10px; }
        .success { background-color: #4CAF50; }
        .file-action { margin-left: 10px; color: #fff; text-decoration: none; }
        .file-action:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>File Manager & Sharing</h1>

        <h3>Connected Users</h3>
        <div class="user-list">
            {% for ip in users %}
                <div>{{ ip }} <button onclick="selectUser('{{ ip }}')">Send File</button></div>
            {% endfor %}
        </div>

        <h3>Upload & Share Files</h3>
        <form class="file-upload" action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <input type="hidden" id="selected_user" name="recipient">
            <button class="btn" type="submit">Upload & Send</button>
        </form>

        <h3>Available Files</h3>
        <div class="file-list">
            {% for file in files %}
                <div class="file">
                    📄 {{ file }} 
                    <a href="/download/{{ file }}" class="file-action">[Download]</a>
                </div>
            {% endfor %}
        </div>

        {% if message %}
            <div class="alert {{ message_type }}">{{ message }}</div>
        {% endif %}
    </div>

    <script>
        function selectUser(ip) {
            document.getElementById("selected_user").value = ip;
            alert("Selected " + ip + " for file transfer.");
        }
    </script>
</body>
</html>
"""

@app.before_request
def track_users():
    ip = request.remote_addr
    if ip not in connected_users:
        connected_users[ip] = time.ctime()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Login required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string(html_code, users=connected_users.keys(), files=files)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if USER_CREDENTIALS.get(username):
            stored_password = USER_CREDENTIALS[username]
            decrypted_password = decrypt_password(stored_password)

            if password == decrypted_password:
                session['username'] = username
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')
        else:
            flash('Invalid username or password', 'error')
    return render_template_string("""
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button class="btn" type="submit">Login</button>
        </form>
    """)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files or request.files['file'].filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    file = request.files['file']
    recipient = request.form['recipient']

    if not recipient or recipient not in connected_users:
        flash('Invalid recipient', 'error')
        return redirect(url_for('index'))

    file_size = len(file.read())
    file.seek(0)

    if file_size > 1 * 1024 * 1024 * 1024 * 1024:
        flash('File too large! Max 1TB.', 'error')
        return redirect(url_for('index'))

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)
    flash(f'File {file.filename} uploaded. Recipient: {recipient}', 'success')

    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)

@app.route('/users')
def list_users():
    return jsonify(list(connected_users.keys()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
