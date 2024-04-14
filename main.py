from flask import Flask
from my_calender import main_blueprint

app = Flask(__name__)
app.register_blueprint(main_blueprint, url_prefix="/")


@app.route("/")
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    print(app.url_map)
    app.run(port=5000, debug=True)