# restructure the project and implement packages to avoid circular imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy #flask tool that converts Python class into database table, and those classes are called models
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
# in order for flask to recognize the model as a database, the following configurations of the app is needed
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'

app.config['SECRET_KEY'] = '5524fae9edda2324151ab336'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app) #encrypt user password, generate hash password instead of plain text
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'

from market import routes
