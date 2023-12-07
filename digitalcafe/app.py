from flask import Flask,redirect
from flask import render_template
from flask import request
from flask import session
from bson.json_util import loads, dumps
from flask import make_response
import database as db
import authentication
import logging
import ordermanagement as om

app = Flask(__name__)

# Set the secret key to some random bytes.
# Keep this really secret!
app.secret_key = b's@g@d@c0ff33!'


logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)


@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products", product_list=product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))

    return render_template('productdetails.html', code=code, product=product)

@app.route('/branches')
def branches():
    branches_list = db.get_branches()

    return render_template('branches.html', page="Branches", branches_list=branches_list)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")

@app.route('/branchdetails')
def branch_details():
    code = request.args.get('code', '')
    branch = db.get_branch(str(code))
    return render_template('branchdetails.html', code=code, branch=branch)

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/auth', methods = ['GET', 'POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')

    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if(is_successful):
        session["user"] = user
        return redirect('/')
    else:
        return render_template('login.html', error="Invalid username or password. Please try again.")

@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')


@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    item=dict()


    item["qty"] = 1
    item["name"] = product["name"]
    item["subtotal"] = product["price"]*item["qty"]

    if(session.get("cart") is None):
        session["cart"]={}

    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')

@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/updatecartitem', methods=['POST'])
def update_cart_item():
    codes = request.form.getlist('code')
    quantities = request.form.getlist('qty')

    for code, quantity in zip(codes, quantities):
        if 'cart' in session and code in session['cart']:
            session['cart'][code]['qty'] = int(quantity)
            session.modified = True

    return redirect('/cart')


@app.route('/removefromcart')
def remove_from_cart():
    code = request.args.get('code', '')

    if 'cart' in session and code in session['cart']:
        del session['cart'][code]
        session.modified = True

    return render_template('cart.html')

@app.route('/checkout')
def checkout():
    om.create_order_from_cart()
    session.pop("cart",None)
    return redirect('/ordercomplete')

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/pastorders')
def past_orders():
    if 'user' not in session:
        return redirect('/login')

    username = session['user']['username']

    orders = om.get_past_orders(username)

    return render_template('pastorders.html', orders=orders)

@app.route('/ordermanagement')
def order_management_db():
    return None

@app.route('/changepassword', methods=['GET', 'POST'])
def changepassword():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Check if new password and confirm password match
        if new_password != confirm_password:
            return render_template('changepassword.html', error="New passwords do not match.")

        # Check if old password is correct
        username = session['user']['username']
        is_valid, user = authentication.login(username, old_password)

        if not is_valid:
            return render_template('changepassword.html', error="Incorrect old password.")

        # Update the password in MongoDB
        db.update_user_password(username, new_password)

        # Redirect to a success page or login page
        return redirect('/changepasswordsuccess')

    return render_template('changepassword.html')

@app.route('/changepasswordsuccess')
def changepasswordsuccess():
    return render_template('changepasswordsuccess.html')

@app.route('/api/products/<int:code>',methods=['GET'])
def api_get_product(code):
    resp = make_response(dumps(db.get_product(code)))
    resp.mimetype = 'application/json'
    return resp

