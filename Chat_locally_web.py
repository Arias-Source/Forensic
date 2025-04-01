from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)

# Store messages and connected users
messages = []
connected_users = {}

HTML_CODE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Private Chat</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #2d3643;
            color: #333;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        header {
            background-color: #374252;
            color: white;
            padding: 15px 20px;
            text-align: center;
            font-size: 24px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            position: relative;
        }
        .menu {
            position: absolute;
            left: 20px; /* Button position */
            top: 15px;
            cursor: pointer;
        }
        .live-users {
            position: absolute;
            right: 20px; /* Adjusted for the new position */
            top: 15px;
            cursor: default;
        }
        .dropdown {
            display: none;
            position: absolute;
            right: 0;
            background-color: white;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            padding: 10px;
            z-index: 1000;
        }
        .dropdown.show {
            display: block;
        }
        #messages {
            list-style-type: none;
            margin: 0;
            padding: 20px;
            flex: 1;
            overflow-y: auto;
            background: gray;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        #messages li {
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 8px;
            position: relative;
            transition: background 0.3s;
        }
        #messages li:hover {
            background: #f1f1f1;
        }
        #form {
            display: flex;
            padding: 10px;
            background: white;
            border-top: 1px solid #ddd;
            box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
        }
        #input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-right: 10px;
            font-size: 16px;
            transition: border 0.3s;
        }
        #input:focus {
            border-color: #4a90e2;
            outline: none;
        }
        #send, #sendLink {
            padding: 10px 15px;
            background-color: #2d3643;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
            margin-left: 5px; /* Space between buttons */
        }
        #send:hover, #sendLink:hover {
            background-color: #2d3643;
        }
        img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }
        iframe {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }
        a {
            color: #2d3643;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        #usernameForm {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            background-color: #252c38;
        }
        #usernameInput {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-bottom: 10px;
            font-size: 16px;
        }
        #setUsername {
            padding: 10px 15px;
            background-color: #4a90e2;
            color: black;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        #setUsername:hover {
            background-color: #24537d;
        }
        #iframeContainer {
            display: none;
            position: fixed;
            top: 50px; /* Fixed position */
            left: 70px; /* Fixed position */
            width: 80%;
            height: 80%;
            background: gray;
            border: 1px solid #ddd;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            z-index: 1000;
        }
        #iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
        #closeIframe {
            position: absolute;
            top: 10px;
            right: 10px;
            background: red;
            color: Black;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div id="usernameForm">
        <input type="text" id="usernameInput" placeholder="Enter your username" />
        <button id="setUsername">Set Username</button>
    </div>
    <header style="display: none;">
        Modern Chat Application
        <div class="menu" onclick="toggleIframe()">Show Website</div> <!-- Changed back to "Show Website" -->
        <div class="live-users">Users: <span id="userCount">0</span></div>
        <div class="dropdown" id="userDropdown">
            <p>Connected Users: <span id="userCountDisplay">0</span></p>
        </div>
    </header>
    <ul id="messages" style="display: none;"></ul>
    <form id="form" action="" style="display: none;">
        <input type="text" id="input" autocomplete="off" placeholder="Type your message..." maxlength="10000" />
        <button id="send">Send</button>
        <button id="sendLink">Send Link</button>
    </form>

    <div id="iframeContainer">
        <button id="closeIframe">Close</button>
        <iframe id="iframe" src="http://192.168.1.212:8000/"></iframe>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.js"></script>
    <script>
        const socket = io();
        const usernameInput = document.getElementById('usernameInput');
        const setUsernameButton = document.getElementById('setUsername');
        const usernameForm = document.getElementById('usernameForm');
        const header = document.querySelector('header');
        const messages = document.getElementById('messages');
        const form = document.getElementById('form');
        const input = document.getElementById('input');
        const userCountDisplay = document.getElementById('userCountDisplay');
        const userCount = document.getElementById('userCount');
        const userDropdown = document.getElementById('userDropdown');
        const iframeContainer = document.getElementById('iframeContainer');
        const iframe = document.getElementById('iframe');
        const sendLinkButton = document.getElementById('sendLink');
        const closeIframeButton = document.getElementById('closeIframe');

        setUsernameButton.addEventListener('click', function() {
            const username = usernameInput.value.trim();
            if (username) {
                socket.emit('set username', username);
                usernameForm.style.display = 'none';
                header.style.display = 'block';
                messages.style.display = 'block';
                form.style.display = 'flex';
            }
        });

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            if (input.value) {
                socket.emit('chat message', input.value);
                input.value = ''; // Clear the input after sending
            }
        });

        sendLinkButton.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent form submission
            const link = input.value.trim();
            if (link) {
                socket.emit('chat message', link); // Send the link as a message
                input.value = ''; // Clear the input after sending
            }
        });

        socket.on('chat message', function(data) {
            const item = document.createElement('li');
            const timestamp = new Date(data.timestamp).toLocaleTimeString();
            item.innerHTML = `[${timestamp}] ${data.username}: ${formatMessage(data.message)}`;
            messages.appendChild(item);
            window.scrollTo(0, document.body.scrollHeight);
        });

        socket.on('user joined', function(username) {
            const item = document.createElement('li');
            item.textContent = `${username} has joined the chat.`;
            messages.appendChild(item);
            window.scrollTo(0, document.body.scrollHeight);
        });

        socket.on('user left', function(username) {
            const item = document.createElement('li');
            item.textContent = `${username} has left the chat.`;
            messages.appendChild(item);
            window.scrollTo(0, document.body.scrollHeight);
        });

        socket.on('message history', function(history) {
            history.forEach(function(data) {
                const item = document.createElement('li');
                const timestamp = new Date(data.timestamp).toLocaleTimeString();
                item.innerHTML = `[${timestamp}] ${data.username}: ${formatMessage(data.message)}`;
                messages.appendChild(item);
            });
            window.scrollTo(0, document.body.scrollHeight);
        });

        socket.on('user count', function(count) {
            userCountDisplay.textContent = count;
            userCount.textContent = count;
        });

        socket.on('connect', function() {
            socket.emit('request user count');
        });

        function formatMessage(msg) {
            if (isImageUrl(msg)) {
                return `<img src="${msg}" alt="Image" />`;
            } else if (isGifUrl(msg)) {
                return `<iframe src="${msg}" width="480" height="442" frameBorder="0" allowFullScreen></iframe>`;
            } else {
                return msg; // Return the message as is if it's not an image or GIF
            }
        }

        function isImageUrl(url) {
            return url.match(/\.(jpeg|jpg|gif|png|bmp|webp)$/) != null || url.startsWith('http');
        }

        function isGifUrl(url) {
            return url.includes("giphy.com/embed/");
        }

        function toggleDropdown() {
            userDropdown.classList.toggle('show');
        }

        function toggleIframe() {
            iframeContainer.style.display = iframeContainer.style.display === 'none' ? 'block' : 'none';
            if (iframeContainer.style.display === 'block') {
                // Set the initial position
                iframeContainer.style.top = '50px'; // Fixed position
                iframeContainer.style.left = '20px'; // Fixed position
                socket.emit('iframe opened'); // Notify others that the iframe is opened
            }
        }

        // Close the iframe
        closeIframeButton.addEventListener('click', function() {
            iframeContainer.style.display = 'none';
        });
    </script>
</body>
</html>

'''

@app.route('/')
def index():
    return render_template_string(HTML_CODE)

@socketio.on('set username')
def handle_set_username(username):
    sid = request.sid
    connected_users[sid] = username
    emit('user joined', username, broadcast=True)
    emit('user count', len(connected_users), broadcast=True)
    emit('message history', messages, to=sid)  # Send the message history to the newly connected client

@socketio.on('chat message')
def handle_message(msg):
    if len(msg) <= 10000:  # Check if the message length is within the limit
        username = connected_users[request.sid]
        timestamp = datetime.now().timestamp()
        message_data = {'username': username, 'message': msg, 'timestamp': timestamp}
        messages.append(message_data)  # Store the message
        emit('chat message', message_data, broadcast=True)  # Broadcast the message to all clients

@socketio.on('disconnect')
def handle_disconnect():
    username = connected_users.pop(request.sid, None)
    if username:
        emit('user left', username, broadcast=True)  # Notify others that the user has left
        emit('user count', len(connected_users), broadcast=True)  # Update user count

@socketio.on('request user count')
def request_user_count():
    emit('user count', len(connected_users))  # Send the current user count to the requesting client

@socketio.on('iframe opened')
def handle_iframe_opened():
    # Notify all users that the iframe has been opened
    emit('iframe opened', broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='192.168.1.46', port=8000)
