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
                ('0', '397', 'bridge street', 'brooklyn', '4th floor', '11201')
                )
        db.execute("INSERT INTO apartments (id, housenumber, street, borough, unitnumber, postalcode) VALUES (?, ?, ?, ?, ?, ?)",
                ('1', '120', 'wilson avenue', 'brooklyn', '3R', '11237')
                )
        res = db.execute("SELECT id from apartments where housenumber = ?", ('120')).fetchall()
        # res = db.fetchone()
        apt_id = res[0]
        
        db.execute("INSERT INTO records (year, status, apartment_id) VALUES (?, ?, ?)",
                ('1984', 'RS', apt_id)
                )
        db.execute("INSERT INTO records (year, status, apartment_id) VALUES (?, ?, ?)",
                ('1985', 'RS', apt_id)
                )
        db.commit()
    

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/search-handling", methods=['POST'])
def search_handling():
    searched = request.form['address_search']
    address_elements = searched.replace(",","").lower().split()
    housenumber = address_elements[0]
    street = f"{address_elements[1]} {address_elements[2]}"
    borough = address_elements[3]

    db = get_db()
    searched_apartments = db.execute('SELECT * from apartments WHERE housenumber = ? AND street = ? AND borough = ?', 
                                     (housenumber, street, borough)).fetchall()
    db.close()

    if searched_apartments:
        return f"{searched_apartments[0]['housenumber']} {searched_apartments[0]['street']}, {searched_apartments[0]['borough']}"
    else:
        return "no match in db"

    # return f"{searched_apartments[0]['housenumber']} {searched_apartments[0]['street']}, {searched_apartments[0]['borough']}"

@app.route("/apartments")
def all_apartments():
    db = get_db()
    apartments = db.execute('SELECT * from apartments').fetchall()
    db.close()
    return render_template('apartments.html', apartments=apartments)

# @app.route("/apartments/<apartment_id>")
# def show_apartment(apartment_id):
#     db = get_db()
#     apartment = db.execute('SELECT * FROM apartments WHERE id = ?', (apartment_id)).fetchone()
#     db.close()
#     return render_template('apartment_record.html', apartment=apartment)

@app.route("/records")
def all_records():
    db = get_db()
    records = db.execute('SELECT * from records').fetchall()
    db.close()
    return render_template('records.html', records=records)

if __name__ == "__main__":
    create_tables()
    seed_db()
    app.run(host="0.0.0.0", port=8080, debug=True)
