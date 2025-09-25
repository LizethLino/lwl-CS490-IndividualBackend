# Imports
from flask import Flask, jsonify, redirect, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime, timezone

# My app
app = Flask(__name__)

# MySQL DB
#evenntually hide your root pass in Git
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Luca15@localhost/sakila'
db = SQLAlchemy(app)

class Customer(db.Model):
    __tablename__ = 'customer'

    customer_id = db.Column(db.Integer, primary_key = True)
    store_id = db.Column(db.Integer, nullable = False)
    first_name = db.Column(db.String(45), nullable = False)
    last_name = db.Column(db.String(45), nullable = False)
    email = db.Column(db.String(50))
    address_id = db.Column(db.Integer, nullable = False)
    active = db.Column(db.Integer, default=1)
    create_date = db.Column(db.DateTime, default = datetime.now(timezone.utc))
    last_update = db.Column(db.DateTime, default = datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

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
    

@app.route("/top5/films", methods=['GET'])
def index():
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

@app.route("/top5/actors", methods=['GET'])
def topActors():
    #view top 5 actors
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

    #select a.actor_id, a.first_name, a.last_name, count(*) as movies 
    #from film f 
    #inner join film_actor fa on f.film_id = fa.film_id 
    #inner join actor a on fa.actor_id = a.actor_id
    #group by a.actor_id
    #order by movies desc;


if __name__ in "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)