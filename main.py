import random
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


API_KEY = "TopSecretAPIKey"

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    # Simply convert the random_cafe data record to a dictionary of key-value pairs.
    return jsonify(cafe=random_cafe.to_dict())



@app.route("/all")
def get_all_cafe():
    cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])

@app.route("/search", methods=["GET"])
def search_by_location():
    location = request.args.get('loc')
    print(location)
    cafes = db.session.query(Cafe).filter_by(location=location)
    try:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])
    except TypeError:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


## HTTP POST - Create Record

@app.route("/add", methods=["POST"])
def add_new_cafe():

    new_cafe = Cafe(
        name=request.form.get("name"),
    map_url = request.form.get("map_url"),
    img_url = request.form.get("img_url"),
    location = request.form.get("location"),
    seats = request.form.get("seats"),
    has_toilet = bool(request.form.get("has_toilet")),
    has_wifi = bool(request.form.get("has_wifi")),
    has_sockets = bool(request.form.get("has_sockets")),
    can_take_calls = bool(request.form.get("can_take_calls")),
    coffee_price = request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"Success": "Successfully added the new Cafe"})


## HTTP PUT/PATCH - Update Record

@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def edit_coffee_price(cafe_id):
    new_coffee_price = request.args.get("new_price")
    try:
        edited_cafe = db.session.query(Cafe).get(cafe_id)
        edited_cafe.coffee_price = new_coffee_price
    except AttributeError:
        return jsonify(error={"Not Found": "Sorry, cafe with that id was not found in database."}),404

    db.session.commit()
    return jsonify(response={"Success": "Successfully updated the price."}),200


## HTTP DELETE - Delete Record

@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    cafe_to_remove = db.session.query(Cafe).get(cafe_id)
    key = request.headers.get('api_key')
    if key == API_KEY and cafe_to_remove:
        db.session.delete(cafe_to_remove)
        db.session.commit()
        return jsonify(response={"Success": "Successfully deleted cafe."}), 200
    elif key != API_KEY:
        return jsonify(response={"Success": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403
    else:
        return jsonify(error={"Not Found": "Sorry, cafe with that id was not found in database."}), 404


if __name__ == '__main__':
    app.run(debug=True)
