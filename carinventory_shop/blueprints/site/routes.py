from flask import Blueprint, render_template, request, flash, redirect


# internal imports 
from carinventory_shop.models import Product, Customer, Order, db, product_schema, products_schema
from carinventory_shop.forms import ProductForm


site = Blueprint('site', __name__, template_folder='site_templates')





#SHOP
@site.route('/')
def shop():

    shop = Product.query.all()
    customers = Customer.query.all()
    orders = Order.query.all()

    shop_stats = {
        'products': len(shop),
        'sales': sum([order.order_total for order in orders]), #order totals  = total cost of specific order
        'customers' : len(customers)
    }

    return render_template('shop.html', shop=shop, stats=shop_stats)





#CREATE
@site.route('/shop/create', methods = ['GET', 'POST'])
def create():

    createform = ProductForm()

    if request.method == 'POST' and createform.validate_on_submit():

        # try: 
        name = createform.name.data
        desc = createform.description.data
        image = createform.image.data
        price = createform.price.data
        quantity = createform.quantity.data 

        shop = Product(name, price, quantity, image, desc)

        db.session.add(shop)
        db.session.commit()

        flash(f"You have successfully created product {name}", category='success')
        return redirect('/')
        
    return render_template('create.html', form=createform)





#UPDATE
@site.route('/shop/update/<id>', methods = ['GET', 'POST'])
def update(id):

    updateform = ProductForm()
    product = Product.query.get(id) 

    if request.method == 'POST' and updateform.validate_on_submit():

        try: 
            product.name = updateform.name.data
            product.description = updateform.description.data
            product.set_image(updateform.image.data, updateform.name.data)
            product.price = updateform.price.data
            product.quantity = updateform.quantity.data 

            

            db.session.commit()

            flash(f"You have successfully updated product {product.name}", category='success')
            return redirect('/')

        except:
            flash("We were unable to process your request. Please try again", category='warning')
            return redirect('/shop/update')
        
    return render_template('update.html', form=updateform, product=product)





#DELETE
@site.route('/shop/delete/<id>')
def delete(id):

    product = Product.query.get(id)

    db.session.delete(product)
    db.session.commit()

    return redirect('/')