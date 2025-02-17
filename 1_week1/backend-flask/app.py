from flask import Flask
from flask_cors import CORS
from routes import study_sessions

def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)
    
    if test_config is None:
        # Load production config
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load test config
        app.config.update(test_config)
    
    # Initialize database
    from db import init_app
    init_app(app)
    
    # Register routes
    study_sessions.load(app)
    
    return app

# Only used when running directly
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 