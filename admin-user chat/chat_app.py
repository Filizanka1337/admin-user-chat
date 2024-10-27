from flask import Flask, render_template_string, request, jsonify
import sqlite3
import threading
import webbrowser
import time

app = Flask(__name__)

# Szablon strony użytkownika (HTML + JavaScript)
user_template = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat z Adminem</title>
    <style>
        body { display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; font-family: Arial, sans-serif; }
        #chatButton { padding: 10px 20px; font-size: 18px; cursor: pointer; }
        #chatPopup { display: block; width: 300px; height: 400px; border: 1px solid #333; background-color: #f9f9f9; }
        #chatHeader { background-color: #333; color: white; padding: 10px; text-align: center; font-weight: bold; }
        #messages { padding: 10px; overflow-y: auto; height: 300px; border-top: 1px solid #333; }
        #messageInput { display: flex; border-top: 1px solid #333; }
        #messageInput input { flex: 1; padding: 5px; border: none; outline: none; }
        #messageInput button { padding: 5px; background-color: #333; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>

<div id="chatPopup">
    <div id="chatHeader">Czat z Adminem</div>
    <div id="messages"></div>
    <div id="messageInput">
        <input type="text" id="userMessage" placeholder="Napisz wiadomość..." onkeypress="handleKeyPress(event)">
        <button onclick="sendMessage()">Wyślij</button>
    </div>
</div>

<script>
    const messages = document.getElementById('messages');

    function loadMessages() {
        fetch('/get_messages')
            .then(response => response.json())
            .then(data => {
                messages.innerHTML = '';
                data.messages.forEach(msg => {
                    const message = document.createElement('div');
                    message.textContent = msg;
                    messages.appendChild(message);
                });
            });
    }

    function sendMessage() {
        const userMessage = document.getElementById('userMessage').value;
        if (userMessage) {
            fetch('/send_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: "Użytkownik: " + userMessage })
            }).then(() => {
                document.getElementById('userMessage').value = '';
                loadMessages();
            });
        }
    }

    function handleKeyPress(event) {
        if (event.key === 'Enter') {
            sendMessage();
            event.preventDefault(); // zapobiega dodaniu nowej linii w polu tekstowym
        }
    }

    setInterval(loadMessages, 1000);
</script>

</body>
</html>
"""

# Szablon strony admina
admin_template = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel Admina - Chat</title>
    <style>
        body { display: flex; flex-direction: column; align-items: center; font-family: Arial, sans-serif; margin: 0; }
        #chatContainer { width: 80%; max-width: 600px; margin-top: 20px; padding: 20px; border: 1px solid #333; background-color: #f9f9f9; }
        #userMessages { height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; }
        #adminMessageInput { display: flex; border-top: 1px solid #333; }
        #adminMessageInput input { flex: 1; padding: 5px; border: none; outline: none; }
        #adminMessageInput button { padding: 5px; background-color: #333; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>

<h1>Panel Admina - Czat z użytkownikiem</h1>

<div id="chatContainer">
    <div id="userMessages"></div>
    <div id="adminMessageInput">
        <input type="text" id="adminMessage" placeholder="Odpowiedz użytkownikowi..." onkeypress="handleKeyPress(event)">
        <button onclick="replyToUser()">Wyślij</button>
    </div>
</div>

<script>
    const userMessages = document.getElementById('userMessages');

    function loadMessages() {
        fetch('/get_messages')
            .then(response => response.json())
            .then(data => {
                userMessages.innerHTML = '';
                data.messages.forEach(msg => {
                    const message = document.createElement('div');
                    message.textContent = msg;
                    userMessages.appendChild(message);
                });
            });
    }

    function replyToUser() {
        const adminMessage = document.getElementById('adminMessage').value;
        if (adminMessage) {
            fetch('/send_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: "Admin: " + adminMessage })
            }).then(() => {
                document.getElementById('adminMessage').value = '';
                loadMessages();
            });
        }
    }

    function handleKeyPress(event) {
        if (event.key === 'Enter') {
            replyToUser();
            event.preventDefault(); // zapobiega dodaniu nowej linii w polu tekstowym
        }
    }

    setInterval(loadMessages, 1000);
</script>

</body>
</html>
"""

# Inicjalizacja bazy danych
def init_db():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, message TEXT)')
    conn.commit()
    conn.close()

@app.route('/user')
def user():
    return render_template_string(user_template)

@app.route('/admin')
def admin():
    return render_template_string(admin_template)

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.json.get('message')
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (message) VALUES (?)', (message,))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route('/get_messages')
def get_messages():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT message FROM messages ORDER BY id')
    messages = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify(messages=messages)

# Uruchomienie dwóch okien przeglądarki (user i admin)
def open_browsers():
    time.sleep(1)  # krótka pauza, aby serwer miał czas na uruchomienie
    webbrowser.open("http://127.0.0.1:5000/user")
    webbrowser.open("http://127.0.0.1:5000/admin")

if __name__ == '__main__':
    init_db()
    threading.Thread(target=open_browsers).start()
    app.run(debug=True)
