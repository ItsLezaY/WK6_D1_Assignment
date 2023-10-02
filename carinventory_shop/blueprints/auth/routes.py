from flask import Blueprint,  render_template, redirect, url_for, flash, request 
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user 

# internal imports
from carinventory_shop.forms import RegisterForm, LoginForm
from carinventory_shop.models import User, db 


auth = Blueprint('auth', __name__, template_folder='auth_templates')



@auth.route('/signup', methods=['GET', 'POST'])

def signup():
    registerform = RegisterForm()

    if request.method == 'POST' and registerform.validate_on_submit():
        first_name = registerform.first_name.data
        last_name = registerform.last_name.data 
        username = registerform.username.data
        email = registerform.email.data
        password = registerform.password.data
        print(email, password)


        if User.query.filter(User.username == username).first():
            flash('Username already exists. Please Try Again', category='warning')
            return redirect('/signup')

        if User.query.filter(User.email == email).first():
            flash('Email already exists. Please try again', category='warning')
            return redirect('/signup')
        
        user = User(username, email, password, first_name=first_name, last_name=last_name)

        db.session.add(user)
        db.session.commit()


        flash(f"You have successfully registered user {username}", category='success')
        return redirect('/signin')
    
    return render_template('sign_up.html', form=registerform)

@auth.route('/signin', methods = ['GET', 'POST'])
def signin():

    loginform = LoginForm()

    if request.method == 'Post' and loginform.validate_on_submit():
        email = loginform.email.data 
        password = loginform.password.data 
        print(email, password)


        user = User.query.filter(User.email == email).first()
        print(user)

        if user and check_password_hash(user.password, password):
            login_user(user)

            flash(f"Successfully logged in user {email}", category='success')
            return redirect('/')
        else:
            flash(f"Invalid Email and/or Password, Please try again", category='warning')
            return redirect('/signin')
        
    return render_template('sign_in.html', form=loginform)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect('/')