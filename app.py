import os
from flask import Flask, render_template, send_file, request

from pgpy import PGPKey, PGPMessage

app = Flask(__name__)

HOME_DIR = os.path.expanduser("~/Desktop/")
OPENPGP_HOME_DIR = os.path.join(HOME_DIR, ".openpgp")

if not os.path.isdir(OPENPGP_HOME_DIR):
    os.makedirs(OPENPGP_HOME_DIR)

@app.route("/", methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        if 'chiffrement' in request.form:
            file = request.files['fichier-chiffrer']
            password = request.form['phrase-passe-chiffrer']
            filename = file.filename

            with open(filename, 'wb') as f:
                f.write(file.read())

            with open(os.path.join(OPENPGP_HOME_DIR, 'temp.key'), 'wb') as f:  # Temporary key
                f.write(PGPKey.from_passphrase(password).armor())  # Generate key from password

            with open(filename + '.pgp', 'wb') as f:
                f.write(PGPMessage.new(filename).encrypt(os.path.join(OPENPGP_HOME_DIR, 'temp.key')).message)

            os.remove(filename)
            os.remove(os.path.join(OPENPGP_HOME_DIR, 'temp.key'))  # Remove temporary key

            return send_file(filename + '.pgp', as_attachment=True)

        elif 'dechiffrement' in request.form:
            file = request.files['fichier-dechiffrer']
            password = request.form['phrase-passe-dechiffrer']
            filename = file.filename

            with open(filename, 'wb') as f:
                f.write(file.read())

            with open(os.path.join(OPENPGP_HOME_DIR, 'temp.key'), 'wb') as f:
                f.write(PGPKey.from_passphrase(password).armor())  # Generate key from password

            with open(filename[:-4], 'wb') as f:
                f.write(PGPMessage.from_file(PGPMessage.new(filename).decrypt(os.path.join(OPENPGP_HOME_DIR, 'temp.key'))).message)

            os.remove(filename)
            os.remove(os.path.join(OPENPGP_HOME_DIR, 'temp.key'))  # Remove temporary key

            return send_file(filename[:-4], as_attachment=True)

    return render_template('index.html')



if __name__ == "__main__":
    app.run(debug=True)
