import secrets
from flask import Flask, render_template
app = Flask(__name__)

app.secret_key = ''

@app.route('/')
def hello_world():
    return render_template('index.html')