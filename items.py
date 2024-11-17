import pymongo
from pymongo import MongoClient
import random

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["shopping_website"]  # Database name
collection = db["items"]  # Collection name

# Define categories with item types and prefixes
categories = {
    "Technology": {
        "prefix": "097",
        "types": ["Laptop", "Smartphone", "Tablet", "Smartwatch", "Wireless Earbuds"]
    },
    "Clothing": {
        "prefix": "064",
        "types": ["T-Shirt", "Jeans", "Jacket", "Sneakers", "Hat"]
    },
    "Home and Living": {
        "prefix": "003",
        "types": ["Sofa", "Dining Table", "Lamp", "Cookware Set", "Bedding Set"]
    },
    "Sports": {
        "prefix": "253",
        "types": ["Basketball", "Soccer Ball", "Yoga Mat", "Tennis Racket", "Running Shoes"]
    }
}

# Sample descriptions for each item type
item_descriptions = {
    "Laptop": "A powerful laptop for professional use.",
    "Smartphone": "A high-end smartphone with advanced features.",
    "Tablet": "A lightweight tablet for on-the-go productivity.",
    "Smartwatch": "A smartwatch with fitness tracking features.",
    "Wireless Earbuds": "Compact wireless earbuds with high sound quality.",
    "T-Shirt": "A comfortable cotton T-shirt.",
    "Jeans": "Stylish denim jeans with a slim fit.",
    "Jacket": "Warm winter jacket for cold weather.",
    "Sneakers": "Casual sneakers for everyday wear.",
    "Hat": "A trendy hat with a unique design.",
    "Sofa": "A cozy sofa with durable upholstery.",
    "Dining Table": "A wooden dining table that seats six.",
    "Lamp": "A modern lamp with adjustable brightness.",
    "Cookware Set": "Non-stick cookware set for everyday cooking.",
    "Bedding Set": "Soft and comfortable bedding set.",
    "Basketball": "Official-size basketball for indoor/outdoor use.",
    "Soccer Ball": "Durable soccer ball for field play.",
    "Yoga Mat": "Non-slip yoga mat for workouts.",
    "Tennis Racket": "Lightweight tennis racket for beginners.",
    "Running Shoes": "Comfortable running shoes with extra support."
}

# Generate a random 10-digit item number with a specific prefix
def generate_item_number(prefix):
    suffix = "".join([str(random.randint(0, 9)) for _ in range(7)])
    return prefix + suffix

# Generate 50 items
items_to_insert = []
for category, details in categories.items():
    for item_type in details["types"]:
        for _ in range(5):  # Generate 5 items per item type
            item_number = generate_item_number(details["prefix"])
            item_quantity = random.randint(1, 10)
            item_price = round(random.uniform(10.0, 200.0), 2)  # Random price between $10 and $200
            item_description = item_descriptions[item_type]
            item_image_url = f"/images/{item_type.lower().replace(' ', '_')}.jpg"  # Placeholder image path

            item = {
                "item_number": item_number,
                "name": item_type,
                "description": item_description,
                "price": item_price,
                "category": category,
                "item_type": item_type,
                "stock": item_quantity,
                "image_url": item_image_url
            }
            
            items_to_insert.append(item)

# Insert items into MongoDB
if items_to_insert:
    collection.insert_many(items_to_insert)
    print(f"Inserted {len(items_to_insert)} items into MongoDB.")
else:
    print("No items to insert.")
