from flask import Flask, render_template, request, g, redirect
import sqlite3

app = Flask(__name__)

DATABASE = '/sqlitedata/database.db'


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
        db.execute("INSERT INTO apartments (housenumber, street, borough, unitnumber, postalcode) VALUES (?, ?, ?, ?, ?)",
                ('120', 'wilson avenue', 'brooklyn', '2R', '11237')
                )
        res = db.execute("SELECT id from apartments where housenumber = ?", ('120',)).fetchone()
        apt_id = res[0]
        
        db.execute("INSERT INTO records (year, status, apartment_id) VALUES (?, ?, ?)",
                ('1984', 'RS', apt_id)
                )
        db.execute("INSERT INTO records (year, status, apartment_id) VALUES (?, ?, ?)",
                ('1985', 'RS', apt_id)
                )
        
        res = db.execute("SELECT id from apartments where housenumber = ? AND unitnumber = ?", ('120', '2R')).fetchone()
        apt_id_two = res[0]

        db.execute("INSERT INTO records (year, status, apartment_id) VALUES (?, ?, ?)",
                ('1990', 'RC', apt_id_two)
                )
        db.execute("INSERT INTO records (year, status, apartment_id) VALUES (?, ?, ?)",
                ('1991', 'RC', apt_id_two)
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
    apartments = db.execute('SELECT * from apartments WHERE housenumber = ? AND street = ? AND borough = ?', 
                                     (housenumber, street, borough)).fetchall()

    if apartments:
        apt_ids = []
        for apartment in apartments:
            apt_ids.append(apartment['id'])
        list_of_records = []
        for id in apt_ids:
            list_of_records.append(db.execute('SELECT * FROM records WHERE apartment_id = ?', (id,)).fetchall())
        db.close()
        records = []
        for record in list_of_records:
            if len(record) > 0:
                for item in record:
                    records.append(item)

        return render_template('records.html', records=records, apartments=apartments)
    else:
        db.close()
        return render_template('records.html', housenumber=housenumber, street=street, borough=borough)


@app.route("/add-record", methods=['POST'])
def add_record():
    year = request.form['year']
    status = request.form['status']
    db = get_db()
    if 'apartment_id' in request.form:
        # apartment_id = request.form['apartment_id']
        # db.execute("INSERT INTO records (year, status, apartment_id) VALUES (?, ?, ?)",
        #                 (year, status, apartment_id)
        #                 )
        # db.commit()
        # records = db.execute('SELECT * FROM records WHERE apartment_id = ?', (apartment_id,)).fetchall()
        # apartments = db.execute('SELECT * FROM apartments WHERE id = ?', (apartment_id,)).fetchall()
        # housenumber = apartments[0]['housenumber']
        # street = apartments[0]['street']
        # borough = apartments[0]['borough']
        # db.close()
        return render_template('records.html', records=records, apartment_id=apartment_id, housenumber=housenumber, street=street, borough=borough)

    elif 'unit' in request.form:
        unitnumber = request.form['unit']
        if 'unitnumber' in request.form:
            unitnumber = request.form['unitnumber']
            
        housenumber = request.form['housenumber']
        street = request.form['street']
        borough = request.form['borough']
        apartment_unit = db.execute('SELECT * FROM apartments WHERE housenumber = ? AND street = ? AND borough = ? AND unitnumber = ?', 
                                (housenumber, street, borough, unitnumber)).fetchall()
        apartment_id = apartment_unit[0]['id']
        db.execute("INSERT INTO records (year, status, apartment_id) VALUES (?, ?, ?)",
                        (year, status, apartment_id)
                        )
        db.commit()

        apartments = db.execute('SELECT * from apartments WHERE housenumber = ? AND street = ? AND borough = ?', 
                                     (housenumber, street, borough)).fetchall()
        apt_ids = []
        for apartment in apartments:
            apt_ids.append(apartment['id'])
        list_of_records = []
        for id in apt_ids:
            list_of_records.append(db.execute('SELECT * FROM records WHERE apartment_id = ?', (id,)).fetchall())
        db.close()
        records = []
        for record in list_of_records:
            if len(record) > 0:
                for item in record:
                    records.append(item)
        db.close()
        return render_template('records.html', records=records, apartments=apartments)

    else:
        housenumber = request.form['housenumber']
        street = request.form['street']
        borough = request.form['borough']
        unitnumber = request.form['unitnumber']
        db.execute("INSERT INTO apartments (housenumber, street, borough, unitnumber) VALUES (?, ?, ?, ?)",
                (housenumber, street, borough, unitnumber)
                )
        db.commit()
        apartment_unit = db.execute('SELECT * FROM apartments WHERE housenumber = ? AND street = ? AND borough = ? AND unitnumber = ?', 
                                (housenumber, street, borough, unitnumber)).fetchall()
        apartment_id = apartment_unit[0]['id']
        db.execute("INSERT INTO records (year, status, apartment_id) VALUES (?, ?, ?)",
                        (year, status, apartment_id)
                        )
        db.commit()
        
        apartments = db.execute('SELECT * from apartments WHERE housenumber = ? AND street = ? AND borough = ?', 
                                     (housenumber, street, borough)).fetchall()
        apt_ids = []
        for apartment in apartments:
            apt_ids.append(apartment['id'])
        list_of_records = []
        for id in apt_ids:
            list_of_records.append(db.execute('SELECT * FROM records WHERE apartment_id = ?', (id,)).fetchall())
        db.close()
        records = []
        for record in list_of_records:
            if len(record) > 0:
                for item in record:
                    records.append(item)
        db.close()
        return render_template('records.html', records=records, apartments=apartments)


@app.route("/apartments")
def all_apartments():
    db = get_db()
    apartments = db.execute('SELECT * from apartments').fetchall()
    db.close()
    return render_template('apartments.html', apartments=apartments)

@app.route("/apartments/<apartment_id>")
def show_apartment(apartment_id):
    db = get_db()
    records = db.execute('SELECT * FROM records WHERE apartment_id = ?', (apartment_id,)).fetchall()
    db.close()
    return render_template('records.html', records=records)

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
