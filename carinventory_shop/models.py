from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin, LoginManager
from datetime import datetime
import uuid 
from flask_marshmallow import Marshmallow 

# internal imports
from .helpers import get_image



db = SQLAlchemy()
login_manager = LoginManager()
ma = Marshmallow() 



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id) 



class User(db.Model, UserMixin):
    user_id = db.Column(db.String, primary_key = True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_added = db.Column(db.DateTime, default = datetime.utcnow)

    def __init__(self, username, email, password, first_name="", last_name=""):
        self.user_id = self.set_id()
        self.first_name = first_name
        self.last_name = last_name 
        self.username = username
        self.email = email
        self.password = self.set_password(password)


    def set_id(self):
        return str(uuid.uuid4())
    
    def get_id(self):
        return str(self.user_id)
    

    def set_password(self, password):
        return generate_password_hash(password)
    

    def __repr__(self):
        return f"<USER: {self.username}"
    

class Product(db.Model):
    prod_id = db.Column(db.String, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    image = db.Column(db.String, nullable = False)
    description = db.Column(db.String(200))
    price = db.Column(db.Numeric(precision=10, scale=2), nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    date_added = db.Column(db.DateTime, default = datetime.utcnow)
    prodord = db.relationship('ProdOrder', backref = 'product', lazy=True)


    def __init__(self, name, price, quantity, image = "", description = ""):
        self.prod_id = self.set_id()
        self.name = name
        self.price = price
        self.quantity = quantity
        self.image = self.set_image(image, name)
        self.description = description

    def set_id(self):
        return str(uuid.uuid4())
    

    def set_image(self, image, name):
        if not image:
            image = get_image(name)
            print("api image", image)

        return image
    
    def decrement_quantity(self, quantity):

        self.quantity -= int(quantity)
        return self.quantity
    
    def increment_quantity(self, quantity):

        self.quantity += int(quantity)
        return self.quantity
    

    def __repr__(self):
        return f"<PRODUCT: {self.name}>"



class Customer(db.Model):
    cust_id = db.Column(db.String, primary_key = True)
    date_created = db.Column(db.DateTime, default = datetime.utcnow())
    prodord  = db.relationship('ProdOrder', backref = 'customer', lazy = True)


    def __init__(self, cust_id):
        self.cust_id = cust_id



class ProdOrder(db.Model):
    prodorder_id = db.Column(db.String, primary_key = True)
    prod_id = db.Column(db.String, db.ForeignKey('product.prod_id'), nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    price = db.Column(db.Numeric(precision = 10, scale = 2), nullable = False)
    order_id = db.Column(db.String,  db.ForeignKey('order.order_id'), nullable = False)
    cust_id = db.Column(db.String, db.ForeignKey('customer.cust_id'), nullable = False)


    def __init__(self, prod_id, quantity, price, order_id, cust_id):
        self.prodorder_id = self.set_id()
        self.prod_id = prod_id
        self.quantity = quantity
        self.price = self.set_price(price, quantity)
        self.order_id = order_id
        self.cust_id = cust_id 


    def set_id(self):
        return str(uuid.uuid4())
    


    def set_price(self, price, quantity):

        quantity = float(quantity)
        price = float(price)

        self.price = quantity * price
        return self.price 
    

    def update_quantity(self, quantity):  

        self.quantity = int(quantity)
        return self.quantity
    


class Order(db.Model):
    order_id = db.Column(db.String, primary_key = True)
    order_total = db.Column(db.Numeric(precision = 10, scale = 2), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow())
    prodorder = db.relationship('ProdOrder', backref = 'order', lazy = True)


    def __init__(self):
        self.order_id = self.set_id()
        self.order_total = 0.00


    def set_id(self):
        return str(uuid.uuid4())
    

    def increment_order_total(self, price):

        self.order_total = float(self.order_total)
        self.order_total += float(price)

        return self.order_total
    
    def decrement_order_total(self, price):

        self.order_total = float(self.order_total)
        self.order_total -= float(price)


        return self.order_total 
    
    def __repr__(self):

        return f"<ORDER: {self.order_id}>"


#Build Schema


class ProductSchema(ma.Schema):
    class Meta: 
        fields = ['prod_id', 'name', 'image', 'description', 'price', 'quantity'] 



product_schema = ProductSchema() 
products_schema = ProductSchema(many = True) 
    

