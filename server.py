# Imports
from flask import Flask, jsonify, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

# My app
app = Flask(__name__)

# MySQL DB
#evenntually hide your root pass in Git
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Luca15@localhost/sakila'
db = SQLAlchemy(app)

class customer(db.model):
    customer_id = db.Column(db.Integer, primary_key = True)
    store_id = db.Column(db.Integer)
    first_name = db.Column(db.String(45), nullable = False)
    last_name = db.Column(db.String(45), nullable = False)
    email = db.Column(db.String(50), nullable = False)
    address_id = db.Column(db.Integer)
    active = db.Column(db.Integer, default=1)
    create_date = db.Column(db.DateTime, default = datetime.now(timezone.utc))
    last_update = db.Column(db.DateTime, default = datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"Customer ID {self.customer_id}"

class film(db.model):
    film_id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(128), nullable = False)
    description = db.Column(db.Text)
    release_year = db.Column(db.Integer)
    language_id = db.Column(db.Integer)
    original_language_id = db.Column(db.Integer)
    rental_duration = db.Column(db.Integer, nullable=False)
    rental_rate = db.Column(db.Numeric(4,2), nullable=False)
    length = db.Column(db.Integer)
    replacement_cost = db.Column(db.Numeric(5,2), nullable=False)
    rating = db.Column(db.Enum('G','PG','PG-13','R','NC-17'))
    special_features = db.Column(db.String(255))
    last_update = db.Column(db.DateTime, default = datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"Film ID {self.film_id}"

#consider this the Landing page but to get to the page we need a "route" which is the beginning line
@app.route("/", methods=['GET'])
def index():
    #view top 5 films
    top_films = db.session.execute("select f.film_id, f.title, c.name" +
                                    "from film f" +
                                    "inner join film_category fc on f.film_id = fc.film_id" +
                                    "inner join category c on fc.category_id = c.category_id")
    result = result.fetchall()
    for row in result:
        print(row)

    #click any of them to view info
    #view top 5 actors
    #view an actor's top 5 rented films

#search for film by name, actor, or genre
#view details of film (GET film)
#rent a film to customer (POST to rental table?)
#@app.route("/Films")

#view all customers (Pagination?)
#search for customers by customer id, first name, or last name
#add new customer (POST to customer table?)
#edit customer info (POST)
#delete customer
#view a customers past and present rental history
#indicate(?) that a customer has returned a film
#@app.route("/Customers")

#@app.route("/getTable",methods=['GET'])
#def get_tables():
#    cursor=con.cursor()
#    cursor.execute("SHOW TABLES;") #queries go here
#    tables=cursor.fetchall()
#    cursor.close()
#    con.close()
#    #print(tables)
#    table_names=[table[0] for table in tables]
#    return jsonify({"tables":table_names})

if __name__ in "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)