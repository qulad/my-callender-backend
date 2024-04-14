from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from my_calender import main_blueprint
import sqlite3

app = Flask(__name__)

app.register_blueprint(main_blueprint, url_prefix="/")

if __name__ == "__main__":
    print(app.url_map)
    
    from core import create_all
    
    create_all()
    
    app.run(port=5000, debug=True)