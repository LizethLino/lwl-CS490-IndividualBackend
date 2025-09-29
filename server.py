# Imports
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, and_, or_, case
from datetime import datetime, timezone

# My app
app = Flask(__name__)

# MySQL DB
#evenntually hide your root pass in Git
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Luca15@localhost/sakila'
db = SQLAlchemy(app)

#tables left to make/consider payment, store, staff, language?

class Country(db.Model):
    __tablename__ = 'country'
    country_id = db.Column(db.Integer, primary_key = True)
    country = db.Column(db.String(50), nullable = False)
    last_update = db.Column(db.DateTime, default = datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"Country ID {self.country_id}"

class City(db.Model):
    __tablename__ = 'city'
    city_id = db.Column(db.Integer, primary_key = True)
    city = db.Column(db.String(50), nullable = False)
    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable = False)
    last_update = db.Column(db.DateTime, default = datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    country = db.relationship('Country', backref = 'Cities')

    def __repr__(self) -> str:
        return f"City ID {self.city_id}"

class Address(db.Model):
    __tablename__ = 'address'
    address_id = db.Column(db.Integer, primary_key = True)
    address = db.Column(db.String(50), nullable = False)
    #address2 i think its all NULL
    district = db.Column(db.String(50), nullable = False)
    city_id = db.Column(db.Integer, db.ForeignKey('city.city_id'), nullable = False)
    postal_code = db.Column(db.String(10))
    phone = db.Column(db.String(20), nullable = False)
    #location geometry datatype
    last_update = db.Column(db.DateTime, default = datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    city = db.relationship('City', backref = 'Addresses')

    def __repr__(self) -> str:
        return f"Address ID {self.address_id}"

class Customer(db.Model):
    __tablename__ = 'customer'

    customer_id = db.Column(db.Integer, primary_key = True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'), nullable = False) #not used yet
    first_name = db.Column(db.String(45), nullable = False)
    last_name = db.Column(db.String(45), nullable = False)
    email = db.Column(db.String(50))
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable = False)
    active = db.Column(db.Integer, default=1)
    create_date = db.Column(db.DateTime, default = datetime.now(timezone.utc))
    last_update = db.Column(db.DateTime, default = datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    #store = db.relationship('Store', backref = 'Customers')
    address = db.relationship('Address', backref = 'Customers')

    def __repr__(self) -> str:
        return f"Customer ID {self.customer_id}"

class Rental(db.Model):
    __tablename__ = 'rental'

    rental_id = db.Column(db.Integer, primary_key=True)
    rental_date = db.Column(db.DateTime, nullable = False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.inventory_id'), nullable = False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable = False)
    return_date = db.Column(db.DateTime)
    staff_id = db.Column(db.Integer, nullable = False)
    last_update = db.Column(db.DateTime, nullable = False, default = datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    inventory = db.relationship('Inventory', backref = 'rentals')
    customer = db.relationship('Customer', backref = 'rentals')

    def __repr__(self) -> str:
        return f"Rental ID {self.rental_id} for inventory {self.inventory_id} to customer {self.customer_id}"

class Inventory(db.Model):
    __tablename__ = 'inventory'

    inventory_id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('film.film_id'), nullable = False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'), nullable = False)
    last_update = db.Column(db.DateTime, nullable = False, default = datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    film = db.relationship('Film', backref = 'Inventories')
    #store = db.relationship('Store', backref = 'Inventories')

    def __repr__(self) -> str:
        return f"Inventory ID {self.inventory_id}: Film {self.film_id} at Store {self.store_id}"

class Actor(db.Model):
    __tablename__ = 'actor'

    actor_id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(45), nullable = False)
    last_name = db.Column(db.String(45), nullable = False)
    last_update = db.Column(db.DateTime, nullable = False, default = datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class FilmActor(db.Model):
    __tablename__ = 'film_actor'

    film_id = db.Column(db.Integer, db.ForeignKey('film.film_id'), primary_key = True)
    actor_id = db.Column(db.Integer, db.ForeignKey('actor.actor_id'), primary_key = True)
    last_update = db.Column(db.DateTime, nullable = False, default = datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    film = db.relationship('Film', backref = 'film_actors')
    actor = db.relationship('Actor', backref = 'film_actors')

class Film(db.Model):
    __tablename__ = 'film'

    film_id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(128), nullable = False)
    description = db.Column(db.Text)
    release_year = db.Column(db.Integer)
    language_id = db.Column(db.Integer, nullable = False)
    original_language_id = db.Column(db.Integer)
    rental_duration = db.Column(db.Integer, nullable=False, default=3)
    rental_rate = db.Column(db.Numeric(4,2), nullable=False, default=4.99)
    length = db.Column(db.Integer)
    replacement_cost = db.Column(db.Numeric(5,2), nullable=False, default=19.99)
    rating = db.Column(db.Enum('G','PG','PG-13','R','NC-17', name='rating_enum'), default='G')
    special_features = db.Column(db.String(255))
    last_update = db.Column(db.DateTime, nullable = False, default = datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"Film ID {self.film_id}: {self.title} ({self.release_year})\n{self.description}"

class FilmCategory(db.Model):
    __tablename__ = 'film_category'
    
    film_id = db.Column(db.Integer, db.ForeignKey('film.film_id'), primary_key = True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), primary_key = True)
    last_update = db.Column(db.DateTime, nullable = False, default = datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    film = db.relationship('Film', backref = 'film_categories')
    category = db.relationship('Category', backref = 'film_categories')

class Category(db.Model):
    __tablename__ = 'category'

    category_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(25), nullable = False)
    last_update = db.Column(db.DateTime, nullable = False, default = datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"Category ID {self.category_id}: {self.name}"
    

@app.route("/")
def index():
    return jsonify([
        {
            "endpoints": [
                "/films/all?film_title=str&actor_first=str&actor_last=str&category_name=str", 
                "/films/top5",
                "/films/<int:myfilm_id>",
                "/actors/top5",
                "/actors/<int:myactor_id>",
                "/actors/<int:myactor_id>/top5films",
                "/customers/all?customer_id=int&first_name=str&last_name=str",
                "/customers/<int:mycustomer_id>",
                "/customers/<int:mycustomer_id>/rental_info"
            ]
        }
    ])

#As a user I want to be able to search a film by name of film, name of an actor, or genre of the film
@app.route("/films/all", methods=["GET"])
def filmsDisplay():
    film_title = request.args.get('film_title',"", type=str)
    actor_first_name = request.args.get('actor_first',"", type=str) #actor
    actor_last_name = request.args.get('actor_last',"", type=str) #actor
    category = request.args.get('category_name',"", type=str)
    page = request.args.get('page', 1, type=int) #query paramter -> /films/all?page=1

    result = db.session.query(Film.film_id, Film.title, Film.description, Film.release_year, Category.name) \
        .join(FilmActor, FilmActor.film_id==Film.film_id) \
        .join(Actor, Actor.actor_id==FilmActor.actor_id) \
        .join(FilmCategory, FilmCategory.film_id == Film.film_id) \
        .join(Category, Category.category_id == FilmCategory.category_id)

    if film_title != "":
        result = result.filter(Film.title.ilike(f"%{film_title}%"))
    if actor_first_name != "":
        result = result.filter(Actor.first_name.ilike(f"%{actor_first_name}%")) #edit
    if actor_last_name != "":
        result = result.filter(Actor.last_name.ilike(f"%{actor_last_name}%")) #edit
    if category != "":
        result = result.filter(Category.name.ilike(f"%{category}%"))

    result = result.order_by(Film.film_id).distinct(Film.film_id)

    pagination = result.paginate(page=page, per_page=10)

    return jsonify(
        {
            "films": [{
                    "film_id": film.film_id,
                    "title": film.title,
                    "description": film.description,
                    "release_year": film.release_year,
                    "category": film.name
                } for film in pagination.items],
            "page_num": pagination.page,
            "total_pages": pagination.pages,
            "total_retrieved": pagination.total
        }
    )

#add more info related to films
#number of copies in inventory
#actors in movie
@app.route("/films/top5", methods=["GET"])
def topFilms():
    #view top 5 films
    subquery = db.session.query(Category.name) \
    .join(FilmCategory, FilmCategory.category_id == Category.category_id) \
    .filter(FilmCategory.film_id == Film.film_id) \
    .limit(1) \
    .correlate(Film).scalar_subquery()
    
    result = db.session.query(Film.film_id, Film.title, subquery.label('category'), func.count(Rental.rental_id).label("rental_count")) \
    .join(Inventory, Inventory.film_id==Film.film_id) \
    .join(Rental, Inventory.inventory_id==Rental.inventory_id) \
    .group_by(Film.film_id) \
    .order_by(func.count(Rental.rental_id).desc()) \
    .limit(5)

    return jsonify([
        {
            "film_id": row.film_id,
            "title": row.title,
            "category": row.category,
            "rental_count": row.rental_count
        }
        for row in result
    ])

@app.route("/films/<int:myfilm_id>", methods=["GET"])
def viewFilm(myfilm_id):
    result = db.session.query(Film.film_id, Film.title, Film.description, Film.release_year, Film.rating, Film.special_features) \
    .filter(Film.film_id==myfilm_id).limit(1)

    return jsonify([
        {
            "film_id": row.film_id,
            "title": row.title,
            "description": row.description,
            "release_year": row.release_year,
            "rating": row.rating,
            "special_features": row.special_features
            #.split(',') on special_features
        }
        for row in result
    ])

@app.route("/actors/top5", methods=["GET"])
def topActors():
    result = db.session.query(Actor.actor_id, Actor.first_name, Actor.last_name, func.count(Actor.actor_id).label("movie_count")) \
    .join(FilmActor, FilmActor.actor_id == Actor.actor_id) \
    .join(Film, Film.film_id == FilmActor.film_id) \
    .group_by(Actor.actor_id) \
    .order_by(func.count(Actor.actor_id).desc()) \
    .limit(5)
    
    return jsonify([
        {
            "actor_id": row.actor_id,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "movie_count": row.movie_count
        }
        for row in result
    ])

@app.route("/actors/<int:myactor_id>", methods=["GET"])
def viewActor(myactor_id):
    result = db.session.query(Actor.actor_id, Actor.first_name, Actor.last_name).filter(Actor.actor_id==myactor_id).limit(1)
    return jsonify([
        {
            "actor_id": row.actor_id,
            "first_name": row.first_name,
            "last_name": row.last_name,
        }
        for row in result
    ])

@app.route("/actors/<int:myactor_id>/top5films", methods=["GET"])
def actorTopFilms(myactor_id):
    subquery = db.session.query(Category.name) \
    .join(FilmCategory, FilmCategory.category_id == Category.category_id) \
    .filter(FilmCategory.film_id == Film.film_id) \
    .limit(1) \
    .correlate(Film).scalar_subquery()
    
    result = db.session.query(Film.film_id, Film.title, subquery.label('category'), func.count(Rental.rental_id).label("rental_count")) \
    .join(FilmActor, Film.film_id==FilmActor.film_id) \
    .join(Actor, Actor.actor_id==FilmActor.actor_id) \
    .join(Inventory, Inventory.film_id==Film.film_id) \
    .join(Rental, Inventory.inventory_id==Rental.inventory_id) \
    .filter(Actor.actor_id==myactor_id) \
    .group_by(Film.film_id) \
    .order_by(func.count(Rental.rental_id).desc()) \
    .limit(5)

    return jsonify([
        {
            "film_id": row.film_id,
            "title": row.title,
            "category": row.category,
            "rental_count": row.rental_count
        }
        for row in result
    ])

#As a user I want the ability to filter/search customers by their customer id, first name or last name.
@app.route("/customers/all", methods=["GET"])
def customersDisplay():
    customer_id = request.args.get('customer_id', 0, type=int)
    first_name = request.args.get('first_name', "", type=str)
    last_name = request.args.get('last_name', "", type=str)
    page = request.args.get('page', 1, type=int) #query paramter -> /customers/all?page=1
    result = db.session.query(Customer.customer_id, Customer.first_name, Customer.last_name, Customer.email)
    
    if customer_id != 0:
        result = result.filter(Customer.customer_id==customer_id)
    if first_name != "":
        result = result.filter(Customer.first_name.ilike(f"%{first_name}%"))
    if last_name != "":
        result = result.filter(Customer.last_name.ilike(f"%{last_name}%"))

    result = result.order_by(Customer.customer_id)
    pagination = result.paginate(page=page, per_page=10)
    
    return jsonify(
        {
            "customers": [{
                    "customer_id": customer.customer_id,
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "email": customer.email
                } for customer in pagination.items],
            "page_num": pagination.page,
            "total_pages": pagination.pages,
            "total_customers": pagination.total
        }
    )

#add rental info i think
@app.route("/customers/<int:mycustomer_id>", methods=["GET"])
def viewCustomer(mycustomer_id):
    result = db.session.query(Customer.customer_id, Customer.first_name, Customer.last_name, Customer.email, Address.address, Address.district, City.city, Country.country) \
    .join(Address, Address.address_id==Customer.address_id) \
    .join(City, City.city_id==Address.city_id) \
    .join(Country, Country.country_id==City.country_id) \
    .filter(Customer.customer_id==mycustomer_id) \
    .limit(1)
    
    return jsonify([
        {
            "customer_id": row.customer_id,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "email": row.email,
            "address": row.address,
            "district": row.district,
            "city": row.city,
            "country": row.country
        } for row in result
    ])

@app.route("/customers/<int:mycustomer_id>/rental_info")
def viewRentalHistory(mycustomer_id):
    nulls_sort = case((Rental.return_date == None, 0), else_=1)
    
    result = db.session.query(Rental.rental_id, Rental.rental_date, Rental.return_date, Film.film_id, Film.title, Film.rental_duration, Film.rental_rate, Film.replacement_cost, Rental.staff_id) \
        .join(Customer, Customer.customer_id==Rental.customer_id) \
        .join(Inventory, Inventory.inventory_id==Rental.inventory_id) \
        .join(Film, Film.film_id==Inventory.film_id) \
        .filter(and_(Customer.customer_id==mycustomer_id, or_(Rental.return_date.is_(None), Rental.return_date.isnot(None)))) \
        .order_by(nulls_sort, Rental.return_date.desc())
    
    return jsonify([
        {
            "rental_id": row.rental_id,
            "rental_date": row.rental_date,
            "return_date": row.return_date,
            "film_id": row.film_id,
            "film_title": row.title,
            "rental_duration": row.rental_duration,
            "rental_rate": row.rental_rate,
            "replacement_cost": row.replacement_cost,
            "staff_id": row.staff_id
        } for row in result
    ])

if __name__ in "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)