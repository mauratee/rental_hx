from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    # print("new web request")
    # return f"hello, world!!! the datetime is {datetime.now()}"
    return render_template('index.html')

@app.route("/search-handling", methods=['POST'])
def search_handling():
    text = request.form['address_search']
    print(text)
    return text


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
