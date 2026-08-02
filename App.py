from flask import Flask
from Config import SECRET_KEY
from Routes import register_routes

app = Flask(__name__)
app.secret_key = SECRET_KEY

register_routes(app)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)