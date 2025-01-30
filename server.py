from flask import Flask, render_template, request, g, jsonify
import sqlite3, os

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
    if len(address_elements) <= 3:
        return render_template('invalidsearch.html')
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
        records = sorted(records, key=lambda x: x['year'])
        apartments = sorted(apartments, key=lambda x: x['unitnumber'])
        return render_template('records.html', records=records, apartments=apartments)
    else:
        db.close()
        return render_template('records.html', housenumber=housenumber, street=street, borough=borough)


@app.route("/add-record", methods=['POST'])
def add_record():
    year = request.form['year']
    status = request.form['status']
    db = get_db()

    if 'unit' in request.form:
        unitnumber = request.form['unit'].lower()
        housenumber = request.form['housenumber']
        street = request.form['street']
        borough = request.form['borough']
        if 'unitnumber' in request.form and request.form['unitnumber'] != '' and request.form['unitnumber'].lower() != unitnumber:
            unitnumber = request.form['unitnumber']
            db.execute("INSERT INTO apartments (housenumber, street, borough, unitnumber) VALUES (?, ?, ?, ?)",
                (housenumber, street, borough, unitnumber)
                )
            db.commit()
        apartment_unit = db.execute('SELECT * FROM apartments WHERE housenumber = ? AND street = ? AND borough = ? AND unitnumber = ?', 
                                (housenumber, street, borough, unitnumber)).fetchall()
        apartment_id = apartment_unit[0]['id']
        
        filing_date = None
        legal_rent = None
        preferential_rent = None
        actual_rent = None
        reasons_difference = None
        lease_dates = None
        if 'filing-date' in request.form and request.form['filing-date'] != '':
            filing_date = request.form['filing-date']
        if 'legal-rent' in request.form and request.form['legal-rent'] != '':
            legal_rent = request.form['legal-rent']
        if 'pref-rent' in request.form and request.form['pref-rent'] != '':
            preferential_rent = request.form['pref-rent']
        if 'actual-rent' in request.form and request.form['actual-rent'] != '':
            actual_rent = request.form['actual-rent']
        if 'reasons-diff' in request.form and request.form['reasons-diff'] != '':
            reasons_difference = request.form['reasons-diff']
        if 'lease-dates' in request.form and request.form['lease-dates'] != '':
            lease_dates = request.form['lease-dates']
        
        db.execute("""INSERT INTO records (year, status, apartment_id, filing_date, legal_rent, preferential_rent, 
                   actual_rent, reasons_difference, lease_dates) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (year, status, apartment_id, filing_date, legal_rent, preferential_rent, actual_rent, reasons_difference, lease_dates)
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
        records = sorted(records, key=lambda x: x['year'])
        apartments = sorted(apartments, key=lambda x: x['unitnumber'])
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

        filing_date = None
        legal_rent = None
        preferential_rent = None
        actual_rent = None
        reasons_difference = None
        lease_dates = None
        if 'filing-date' in request.form and request.form['filing-date'] != '':
            filing_date = request.form['filing-date']
        if 'legal-rent' in request.form and request.form['legal-rent'] != '':
            legal_rent = request.form['legal-rent']
        if 'pref-rent' in request.form and request.form['pref-rent'] != '':
            preferential_rent = request.form['pref-rent']
        if 'actual-rent' in request.form and request.form['actual-rent'] != '':
            actual_rent = request.form['actual-rent']
        if 'reasons-diff' in request.form and request.form['reasons-diff'] != '':
            reasons_difference = request.form['reasons-diff']
        if 'lease-dates' in request.form and request.form['lease-dates'] != '':
            lease_dates = request.form['lease-dates']
        
        db.execute("""INSERT INTO records (year, status, apartment_id, filing_date, legal_rent, preferential_rent, 
                   actual_rent, reasons_difference, lease_dates) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (year, status, apartment_id, filing_date, legal_rent, preferential_rent, actual_rent, reasons_difference, lease_dates)
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
        records = sorted(records, key=lambda x: x['year'])
        apartments = sorted(apartments, key=lambda x: x['unitnumber'])
        return render_template('records.html', records=records, apartments=apartments)


@app.route('/get_token')
def get_token():
    mapbox_token = os.getenv('MPBX_API_KEY')
    return jsonify({'mapbox_token': mapbox_token})


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
    # create_tables()
    # seed_db()
    app.run(host="0.0.0.0", port=8080, debug=True)
