import json
from flask import Flask, request

app = Flask(__name__)

app.secret_key = '36d37ff024c80147d78bdd5401aa7f76f55'


client_secrets_file = "static/client_secret.json"

with open(client_secrets_file) as cs_file:
    client_secrets = json.load(cs_file)
    redirect_uri = client_secrets['web']['redirect_uris'][0]
    port = redirect_uri.split(':')[-1].split('/')[0]
    host = redirect_uri.split(':'+port)[0].split('//')[-1]
    port = int(port)

@app.route('/authorize')
def authorize():
    return f"""<h1>code: {request.args.get('code')}</h1>"""

if __name__ == '__main__':
    print(f"host: {host} || port: {port}")
    app.run(host, port, debug=True)