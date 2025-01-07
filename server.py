from flask import Flask, render_template, request, g
import sqlite3

app = Flask(__name__)

DATABASE = 'database.db'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def create_tables():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def seed_db():
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO apartments (id, housenumber, street, borough, unitnumber, postalcode) VALUES (?, ?, ?, ?, ?, ?)",
                ('0', '397', 'Bridge Street', 'Brooklyn', '4th floor', '11201')
                )
        db.execute("INSERT INTO apartments (id, housenumber, street, borough, unitnumber, postalcode) VALUES (?, ?, ?, ?, ?, ?)",
                ('1', '120', 'Wilson Avenue', 'Brooklyn', '3R', '11237')
                )
        db.commit()
    

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/search-handling", methods=['POST'])
def search_handling():
    text = request.form['address_search']
    address_elements = text.replace(",","").split()
    housenumber = address_elements[0]
    street = f"{address_elements[1]} {address_elements[2]}"
    # for element in address_elements:
    #     print(element)
    # print(text)
    return f"{housenumber} {street}"

@app.route("/apartments")
def show_apartments():
    db = get_db()
    apartments = db.execute('SELECT * from apartments').fetchall()
    db.close()
    return render_template('apartments.html', apartments=apartments)




if __name__ == "__main__":
    create_tables()
    seed_db()
    app.run(host="0.0.0.0", port=8080, debug=True)
