from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests

app = Flask(__name__)
app.secret_key = 'sua-chave-secreta'  # Altere para uma chave secreta real

SERVER_URL = 'http://localhost:8888'  # URL do servidor de chat

@app.route('/')
def index():
    if 'client_id' in session:
        return redirect(url_for('user_interface'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        response = requests.post(f'{SERVER_URL}/register')
        return jsonify(response.json())
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        client_id = request.form['client_id']
        response = requests.post(f'{SERVER_URL}/login', json={'client_id': client_id})
        if response.status_code == 200:
            session['client_id'] = client_id
            return redirect(url_for('user_interface'))
        return 'Falha no login, tente novamente.', 400
    return render_template('login.html')

@app.route('/user_interface')
def user_interface():
    if 'client_id' not in session:
        return redirect(url_for('index'))
    return render_template('user_interface.html', client_id=session['client_id'])

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    response = requests.post(f'{SERVER_URL}/send_message', json=data)
    return jsonify(response.json())

@app.route('/create_group', methods=['POST'])
def create_group():
    data = request.json
    response = requests.post(f'{SERVER_URL}/create_group', json=data)
    return jsonify(response.json())

@app.route('/send_group_message', methods=['POST'])
def send_group_message():
    data = request.json
    response = requests.post(f'{SERVER_URL}/send_group_message', json=data)
    return jsonify(response.json())

@app.route('/logout')
def logout():
    session.pop('client_id', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=8000)
