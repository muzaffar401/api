from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import bcrypt
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
from pydantic import BaseModel

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": f"Internal server error: {str(exc)}"}
    ) 

# In-memory storage for serverless deployment
users_data = {}
products_data = {}
orders_data = []

# Initialize with default data
def initialize_data():
    global users_data, products_data, orders_data
    
    # Default products
    products_data = {
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
    
    # Default admin user
    users_data = {
        "admin@grocery.com": {
            "username": "Admin",
            "password": "$2a$12$Gv.SiLx.fu.gmtTwALffwO9xpCXfS.lQIkqYqS5Nj7GmeJIe.dSSK",  # password: admin123
            "role": "admin",
            "created_at": "2024-01-01T00:00:00"
        }
    }
    
    # Initialize empty orders
    orders_data = []

# Initialize data on startup
initialize_data()

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
    return {
        "success": True,
        "message": "Welcome to Grocery Store API!",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {
        "success": True,
        "status": "healthy",
        "message": "API is running"
    }

def get_users():
    return users_data

@app.get("/users")
def get_users_endpoint():
    try:
        users = get_users()
        return {"success": True, "users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading users: {str(e)}")

@app.post("/users")
def create_user(user: User):
    try:
        if user.email in users_data:
            raise HTTPException(status_code=400, detail="Email already registered")
        if not validate_email_format(user.email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        hashed = hash_password(user.password)
        users_data[user.email] = {
            "username": user.username,
            "password": hashed.decode('utf-8'),
            "role": "user",
            "created_at": datetime.now().isoformat()
        }
        return {"success": True, "message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/login")
def login(creds: LoginCreds):
    try:
        if creds.email not in users_data:
            raise HTTPException(status_code=400, detail="Email not found")
        stored_password = users_data[creds.email]['password']
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        if verify_password(creds.password, stored_password):
            return {
                "success": True,
                "role": users_data[creds.email]['role'], 
                "username": users_data[creds.email]['username'],
                "email": creds.email
            }
        raise HTTPException(status_code=400, detail="Incorrect password")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/products")
def get_products():
    return products_data

@app.post("/products")
def add_product(product: Product):
    if product.name in products_data:
        raise HTTPException(status_code=400, detail="Product already exists")
    products_data[product.name] = {"price": product.price, "unit": product.unit}
    return {"success": True, "message": "Product added successfully"}

class ProductUpdate(BaseModel):
    price: float
    unit: str

@app.put("/products/{name}")
def update_product(name: str, product: ProductUpdate):
    if name not in products_data:
        raise HTTPException(status_code=404, detail="Product not found")
    products_data[name] = {"price": product.price, "unit": product.unit}
    return {"success": True, "message": "Product updated successfully"}

@app.delete("/products/{name}")
def delete_product(name: str):
    if name not in products_data:
        raise HTTPException(status_code=404, detail="Product not found")
    del products_data[name]
    return {"success": True, "message": "Product deleted successfully"}

@app.get("/orders")
def get_orders():
    return orders_data

@app.post("/orders")
def create_order(order: Order):
    orders_data.append(order.dict())
    return {"success": True, "message": "Order created successfully"}

@app.put("/orders/{order_id}")
def update_order(order_id: str, update: OrderUpdate):
    for i, o in enumerate(orders_data):
        if o['order_id'] == order_id:
            orders_data[i]['status'] = update.status
            return {"success": True, "message": "Order status updated successfully"}
    raise HTTPException(status_code=404, detail="Order not found")