from market import app, db
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from flask_login import login_user, logout_user, login_required, current_user

# A route in the context of web development (and specifically Flask) is essentially a URL path
# decorators are like functions that execute before the actual function itself
@app.route('/')    #decorators, '/' suggests root url
@app.route('/home')

def home_page():
    return render_template('home.html')

# This decorator binds a specific URL (or route) to a Python function, which is called a view function.
# When a user navigates to the defined URL, the corresponding view function is executed.
# #dynamic routes
# @app.route('/about/<username>')
# def about_page(username):
#     return f'<h1>This is the about page of {username}</h1>'


# send data to the html from route
@app.route('/market', methods=['GET', 'Post'])
@login_required # execute before the market_page function is called
def market_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    if request.method == 'POST':    # differentiate POST and GET method access to avoid Confirm Form Resubmission everytime we refresh the page
        # Purchase Item Logic
        purchased_item = request.form.get('purchased_item')     #defined in items_modals.html
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Congratulations! You purchased {p_item_object.name} for {p_item_object.price}$", category='success')
            else:
                flash(f"You don't have enough money to purchase {p_item_object.name}", category='danger')


        # Sell Item Logic
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"Congratulations! You Sold {s_item_object.name} for {s_item_object.price}$", category='success')
            else:
                flash(f"Something went wrong with selling {s_item_object.name}", category='danger')

        return redirect(url_for('market_page'))

    if request.method == 'GET':
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items, selling_form=selling_form)

@app.route('/register', methods=['GET', 'POST'])  #add POST method into the route to allow the user's to POST data to the route
def register_page():
    form = RegisterForm()
    # flask validation
    if form.validate_on_submit(): #check whether the user has checked the submit button
                                  #and whether the conditions set by the validators are met
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully, you are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}: #if there are errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger') #display err msg on html instead of terminal

    return render_template('register.html', form=form)
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as : {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match! Please try again.', category='danger')


    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out.', category='info')
    return redirect(url_for('home_page'))

