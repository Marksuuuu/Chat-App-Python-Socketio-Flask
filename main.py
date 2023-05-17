from flask import Flask, render_template, request, redirect, url_for, jsonify, json, session
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, engineio_logger=True, cors_allowed_origins='*')

# Store the mapping of clients and their names
clients = {}

photo = ''
username = ''

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form_username = request.form['username']
        form_password = request.form['password']

        if form_username == '' and form_password == '':
            return """<script>
                            alert('Error')
                            </script>"""
        else:

            url = f"http://hris.teamglac.com/api/users/login?u={form_username}&p={form_password}"
            response = requests.get(url).json()

            if response['result'] == False:
                return """<script>
                            alert('Error')
                            </script>"""
            else:
                user_data = response["result"]
                session['fullname'] = user_data['fullname']
                global username
                username = session['fullname'] = user_data['fullname']
                photo_url = session['photo_url'] = user_data['photo_url']

                global photo
                if photo_url == False:
                    photo = """/assets/images/pngegg.png"""
                else:
                    hris = "http://hris.teamglac.com/"
                    session['photo_url'] = hris + user_data['photo_url']
                    photo = session['photo_url'] = hris + user_data['photo_url']
        return redirect(url_for('index', success=True))

    else:
        # Display the login form
        return render_template('login-auth.html')

@app.route('/index')
def index():
    return render_template('chat.html', fullname_var=session['fullname'], photo=photo)

@app.route('/logout')
def logout():
    # Clear the session and redirect to the login page
    session.clear()
    return redirect(url_for('login', success=True))

@socketio.on('connect')
def handle_connect():
    if 'fullname' in session:
        fullname_var = session['fullname']
        photo = session['photo_url']
        socketio.emit('handle_data', {'fullname_var': fullname_var, 'photo': photo})
        print('Client connected:', fullname_var)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in clients:
        del clients[request.sid]
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    sender_name = clients.get(request.sid)
    print('sender data', sender_name)
    photo_var = session['photo_url']
    sender_name_here = session['fullname']
    is_sender = sender_name == session['fullname']
    emit('message', {'sender': sender_name_here, 'message': data['message'], 'is_sender': is_sender, 'photo_var': photo_var}, broadcast=True)

@socketio.on('join')
def handle_join(data):
    clients[request.sid] = data['name']
    emit('join', {'message': f'{data["name"]} has joined the chat'}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='10.0.2.150', port='5000', debug=True)
