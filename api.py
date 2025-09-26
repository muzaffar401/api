from fastapi import FastAPI, HTTPException
import json
import os
import bcrypt
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
from pydantic import BaseModel

app = FastAPI() 

USERS_FILE = "users.json"
PRODUCTS_FILE = "products.json"
ORDERS_FILE = "orders.json"

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def validate_email_format(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

class User(BaseModel):
    username: str
    email: str
    password: str

class LoginCreds(BaseModel):
    email: str
    password: str

class Product(BaseModel):
    name: str
    price: float
    unit: str

class Order(BaseModel):
    order_id: str
    email: str
    username: str
    items: dict
    subtotal: float
    discount_amount: float
    tax_amount: float
    total: float
    status: str = "pending"
    date: str = datetime.now().isoformat()

class OrderUpdate(BaseModel):
    status: str

@app.get("/")
def read_root():
    return {"message": "Welcome to Grocery Store API! Docs at /docs"}

@app.get("/users")
def get_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
            return users
    return {}

@app.post("/users")
def create_user(user: User):
    users = get_users()
    if user.email in users:
        raise HTTPException(status_code=400, detail="Email already registered")
    if not validate_email_format(user.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    hashed = hash_password(user.password)
    users[user.email] = {
        "username": user.username,
        "password": hashed.decode('utf-8'),
        "role": "user",
        "created_at": datetime.now().isoformat()
    }
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)
    return {"success": True}

@app.post("/login")
def login(creds: LoginCreds):
    users = get_users()
    if creds.email not in users:
        raise HTTPException(status_code=400, detail="Email not found")
    stored_password = users[creds.email]['password']
    if isinstance(stored_password, str):
        stored_password = stored_password.encode('utf-8')
    if verify_password(creds.password, stored_password):
        return {"role": users[creds.email]['role'], "username": users[creds.email]['username']}
    raise HTTPException(status_code=400, detail="Incorrect password")

@app.get("/products")
def get_products():
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "r") as f:
            return json.load(f)
    default = {
        "apple": {"price": 100, "unit": "kg"},
        "banana": {"price": 50, "unit": "dozen"},
        "milk": {"price": 120, "unit": "litre"},
        "bread": {"price": 80, "unit": "loaf"},
        "egg": {"price": 15, "unit": "piece"},
        "orange": {"price": 60, "unit": "kg"},
        "mango": {"price": 150, "unit": "kg"},
        "potato": {"price": 30, "unit": "kg"},
        "tomato": {"price": 40, "unit": "kg"},
        "onion": {"price": 25, "unit": "kg"},
        "carrot": {"price": 50, "unit": "kg"},
        "cucumber": {"price": 20, "unit": "kg"},
        "spinach": {"price": 30, "unit": "kg"},
        "cauliflower": {"price": 40, "unit": "piece"},
        "broccoli": {"price": 60, "unit": "kg"},
        "juice": {"price": 150, "unit": "litre"},
        "biscuits": {"price": 80, "unit": "packet"},
        "chips": {"price": 50, "unit": "packet"},
        "soap": {"price": 60, "unit": "piece"},
        "shampoo": {"price": 200, "unit": "bottle"},
        "detergent": {"price": 120, "unit": "kg"},
        "toothpaste": {"price": 90, "unit": "tube"},
        "oil": {"price": 200, "unit": "litre"},
        "salt": {"price": 20, "unit": "kg"},
        "sugar": {"price": 60, "unit": "kg"},
        "tea": {"price": 200, "unit": "packet"},
        "coffee": {"price": 300, "unit": "packet"},
        "butter": {"price": 250, "unit": "pack"},
        "cheese": {"price": 400, "unit": "kg"},
        "yogurt": {"price": 100, "unit": "litre"},
        "chicken": {"price": 300, "unit": "kg"},
        "fish": {"price": 500, "unit": "kg"},
        "rice": {"price": 80, "unit": "kg"},
        "wheat": {"price": 45, "unit": "kg"},
        "pasta": {"price": 100, "unit": "packet"},
        "noodles": {"price": 70, "unit": "packet"},
        "jam": {"price": 150, "unit": "jar"},
        "honey": {"price": 300, "unit": "jar"},
        "cereal": {"price": 200, "unit": "box"},
        "chocolate": {"price": 100, "unit": "bar"}
    }
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(default, f, indent=4)
    return default

@app.post("/products")
def add_product(product: Product):
    products = get_products()
    if product.name in products:
        raise HTTPException(status_code=400, detail="Product already exists")
    products[product.name] = {"price": product.price, "unit": product.unit}
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=4)
    return {"success": True}

class ProductUpdate(BaseModel):
    price: float
    unit: str

@app.put("/products/{name}")
def update_product(name: str, product: ProductUpdate):
    products = get_products()
    if name not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    products[name] = {"price": product.price, "unit": product.unit}
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=4)
    return {"success": True}

@app.delete("/products/{name}")
def delete_product(name: str):
    products = get_products()
    if name not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    del products[name]
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=4)
    return {"success": True}

@app.get("/orders")
def get_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    return []

@app.post("/orders")
def create_order(order: Order):
    orders = get_orders()
    orders.append(order.dict())
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=4)
    return {"success": True}

@app.put("/orders/{order_id}")
def update_order(order_id: str, update: OrderUpdate):
    orders = get_orders()
    for i, o in enumerate(orders):
        if o['order_id'] == order_id:
            orders[i]['status'] = update.status
            with open(ORDERS_FILE, "w") as f:
                json.dump(orders, f, indent=4)
            return {"success": True}
    raise HTTPException(status_code=404, detail="Order not found")