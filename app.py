from flask import Flask
from flask_restful import Api
from routes import initialize_routes

app = Flask(__name__)
api = Api(app)

# Add resources to the API
initialize_routes(api)

if __name__ == '__main__':
    app.run(debug=True)