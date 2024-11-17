from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from bson.objectid import ObjectId

app = Flask(__name__)

load_dotenv()

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/shopping_website"  # Update with your MongoDB URI
mongo = PyMongo(app)

# Set a secret key for session management
app.secret_key = 'your_secret_key_here'

@app.route("/api/get-key")
def get_key():
    return jsonify({"apiKey": os.getenv("GML_API_KEY")})

@app.route("/")
def index():
    # Fetch all categories to display in sidebar
    items = mongo.db.items.find()
    categories = mongo.db.items.distinct("category")
    #grab total cart items for current user in session
    user = mongo.db.users.find_one({"username": session.get("username")})
    total = 0
    if user:
        total = len(user["cartItems"])
    return render_template("index.html", categories=categories, items=items, total=total)

@app.route("/technology")
def technology():
    # Fetch items within the "Technology" category
    items = list(mongo.db.items.find({"category": "Technology"}).limit(15))
    return render_template("index.html", items=items, categories=["Technology"])

@app.route("/clothing")
def clothing():
    # Fetch items within the "Clothing" category
    items = list(mongo.db.items.find({"category": "Clothing"}).limit(15))
    return render_template("index.html", items=items, categories=["Clothing"])

@app.route("/living")
def living():
    # Fetch items within the "Home and Living" category
    items = list(mongo.db.items.find({"category": "Home and Living"}).limit(15))
    return render_template("index.html", items=items, categories=["Home and Living"])

@app.route("/sports")
def sports():
    # Fetch items within the "Sports" category
    items = list(mongo.db.items.find({"category": "Sports"}).limit(15))
    return render_template("index.html", items=items, categories=["Sports"])

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if request.method == "POST":
        item_id = request.form.get("item_id")
        item = mongo.db.items.find_one({"_id": ObjectId(item_id)})
        if item:
            # Check if the item is already in the user's cart
            user = mongo.db.users.find_one({"username": session.get("username")})
            
            if user and not any(cart_item["_id"] == ObjectId(item_id) for cart_item in user["cartItems"]):
            # Add the item to the user's cart in the database
                mongo.db.users.update_one(
                    {"username": session.get("username")},
                    {"$push": {"cartItems": item}}
                )
                return redirect(url_for("index"))
            else:
                return "Item already in cart", 400
        else:
            return "Item not found", 404
        
@app.route("/remove", methods=["POST"])
def remove():
    if request.method == "POST":
        item_id = request.form.get("item_id")
        item = mongo.db.items.find_one({"_id": ObjectId(item_id)})
        if item:
            # Add the item to the user's cart in the database
            mongo.db.users.update_one(
                {"username": session.get("username")},
                {"$pull": {"cartItems": item}}
            )
            return redirect(url_for("cart"))
        else:
            return "Item not found", 404
        
@app.route("/checkout", methods=["POST"])
def checkout():
    if request.method == "POST":
        username = session.get("username")
        user = mongo.db.users.find_one({"username": username})
        # for each item in the cart remove 1 from the stock
        for item in user.get("cartItems", []):
            if item['stock'] == 0:
                message = "Item is out of stock", item['name']
                return render_template("cart.html", message=message)
            else:
                mongo.db.items.update_one(
                    {"_id": item["_id"]},
                    {"$inc": {"stock": -1}}
                )

        if not user:
            return "User not found", 404

        cart_items = user.get("cartItems", [])
        
        # Perform the update
        mongo.db.users.update_one(
            {"username": username},
            {
                "$push": {"purchases": {"$each": cart_items}},  # Add cart items to purchases
                "$set": {"cartItems": []}  # Clear the cart
            }
        )

        return redirect(url_for("index"))

        
@app.route("/cart")
def cart():
    # Fetch the user's cart items from the database
    user = mongo.db.users.find_one({"username": session.get("username")})
    cart_items = user.get("cartItems", []) if user else []
    return render_template("cart.html", cart_items=cart_items)

@app.route("/profile")
def profile():
    # Fetch the user's profile information from the database
    user = mongo.db.users.find_one({"username": session.get("username")})
    purchases = user.get("purchases", []) if user else []
    
    # Initialize total and rounded to default values
    total = 0
    rounded = 0
    
    if purchases:  # Check if there are purchases
        for purchase in purchases:
            total += purchase.get("price", 0)  # Ensure a default price of 0 if 'price' is missing
        rounded = round(total, 2)
    
    return render_template("profile.html", user=user, purchases=purchases, rounded=rounded)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form.get("username")
        password = request.form.get("password")
        first_name = request.form.get("firstName")
        last_name = request.form.get("lastName")
        email = request.form.get("email")
        location = request.form.get("location")

        # Check if user already exists
        if mongo.db.users.find_one({"username": username}):
            return redirect(url_for('login'))
        
        items = []
        purchases = []
        
        #convert password into hashed password
        password = generate_password_hash(password)
        
        # Insert new user into MongoDB
        mongo.db.users.insert_one({
            'username': username, 
            'password': password,
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'location': location,
            'cartItems': items,
            "purchases": purchases
        })

        # Set session data
        session['logged_in'] = True
        session['username'] = username

        return redirect(url_for('index'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = mongo.db.users.find_one({"username": username})
        
        if user:
            password_match = check_password_hash(user['password'], password)
            if password_match:
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear session data
    session.clear()
    return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True)
