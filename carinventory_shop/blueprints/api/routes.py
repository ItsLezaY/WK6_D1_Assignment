from flask import Blueprint, request, jsonify 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity 

#internal imports 
from carinventory_shop.models import Customer, Product, ProdOrder, Order, db, product_schema, products_schema 



api = Blueprint('api', __name__, url_prefix = '/api')


@api.route('/token', methods = ['GET', 'POST'])
def token():

    data = request.json

    if data:
        client_id = data['client_id']
        access_token = create_access_token(identity=client_id) 
        return {
            'status' : 200,
            'access_token' : access_token 
        }
    
    else:
        return {
            'status': 400,
            'message': 'Missing Client Id. Try Again'
        }
    

#creating our READ data request
@api.route('/shop')
@jwt_required() #friendo decorator - makes sure access token created is present
def get_shop():

    shop = Product.query.all() 

    response = products_schema.dump(shop) #turns lists of objs > list of dicts
    return jsonify(response) #jsonify stringifies list to send to frontend


# #creating our READ data request for orders (GET)
@api.route('/order/<cust_id>')
@jwt_required()
def get_order(cust_id): #pass same id as the parameter in the function

    prodorder = ProdOrder.query.filter(ProdOrder.cust_id == cust_id).all()


    data = []

    #traverse to grab all products from one another
    for order in prodorder: 


        product = Product.query.filter(Product.prod_id == order.prod_id).first()

        prod_data = product_schema.dump(product)

        prod_data['quantity'] = order.quantity
        prod_data['order_id'] = order.order_id
        prod_data['id'] = order.prodorder_id

        data.append(prod_data)


    return jsonify(data)


# #create our CREATE data request for orders (POST)
@api.route('/order/create/<cust_id>', methods = ['POST'])
@jwt_required()
def create_order(cust_id):

    data = request.json

    customer_order = data['order']
    print(customer_order)

    customer = Customer.query.filter(Customer.cust_id == cust_id).first()
    if not customer:
        customer = Customer(cust_id)
        db.session.add(customer)

    order = Order()
    db.session.add(order)

    for product in customer_order:

        prodorder = ProdOrder(product['prod_id'], product['quantity'], product['price'], order.order_id, customer.cust_id)
        db.session.add(prodorder)

        order.increment_order_total(prodorder.price)


        current_product = Product.query.filter(Product.prod_id == product['prod_id']).first()
        current_product.decrement_quantity(product['quantity'])


    db.session.commit()


    return {
        'status': 200,
        'message': 'New Order was created!'
    }



# #create our UPDATE route for our orders (PUT)
@api.route('/order/update/<order_id>', methods = ['PUT', 'POST']) 
@jwt_required()
def update_order(order_id):

    # try: 

    data = request.json
    new_quantity = int(data['quantity'])
    prod_id = data['prod_id']


    prodorder = ProdOrder.query.filter(ProdOrder.order_id == order_id, ProdOrder.prod_id == prod_id).first()
    order = Order.query.get(order_id) 
    product = Product.query.get(prod_id)


    prodorder.set_price(product.price, new_quantity)

    diff = abs(prodorder.quantity - new_quantity)


    if prodorder.quantity < new_quantity: 
        product.decrement_quantity(diff)
        order.increment_order_total(prodorder.price)

    elif prodorder.quantity > new_quantity:
        product.increment_quantity(diff)
        order.decrement_order_total(prodorder.price)


    prodorder.update_quantity(new_quantity)

    db.session.commit()

    return {
        'status': 200,
        'message': 'Order was successfully updated!'
    }



# #DELETE route for order
@api.route('/order/delete/<order_id>', methods = ['DELETE'])
@jwt_required()
def delete_item_order(order_id):

    data = request.json
    prod_id = data['prod_id']


    prodorder = ProdOrder.query.filter(ProdOrder.order_id == order_id, ProdOrder.prod_id == prod_id).first()

    order = Order.query.get(order_id)
    product = Product.query.get(prod_id)


    order.decrement_order_total(prodorder.price)
    product.increment_quantity(prodorder.quantity)

    db.session.delete(prodorder)
    db.session.commit()

    return {
        'status' : 200,
        'message': 'Order was successfully deleted!'
    }