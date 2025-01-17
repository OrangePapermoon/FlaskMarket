from market import db, login_manager
from market import bcrypt
from flask_login import UserMixin

#add this line to allow your flask application (after the user has login in)
# to know whether the user is authenticated or not every time a page is refreshed
@login_manager.user_loader
def load_user(user_id):
    if not user_id or user_id == 'None':
        return None
    return User.query.get(int(user_id))

# Model relationships
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    # Should encrypt plain passwords for security reasons
    password_hash = db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=1000)
    # relationship field between User and Item
    items = db.relationship('Item', backref='owned_user', lazy=True)

    @property
    def prettier_budget(self):
        if len(str(self.budget)) >= 4:
            return f'{str(self.budget)[:-3]},{str(self.budget)[-3:]}$'
        else:
            return f"{self.budget}$"

    @property   # getter and setter, getter provides controlled access to a private or protected attribute.
                # setter allows you to validate or modify the value before assigning it to the attribute.
    # The password setter encapsulates the logic for securely handling passwords, ensuring that only hashed passwords are stored.
    # The actual password_hash attribute is hidden from direct access, making it secure.

    def password(self):
        return self.password #get password1 filled by user, because in routes.py, password1(in forms.py)
                             # was passed to users as their password attribute


    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

        # You don’t need to explicitly call the setter like a method (e.g., user_to_create.password('plaintext'))
        # because Python automatically does this for you when you assign a value to the password property.
        # When you assign a value to password (e.g., password=form.password1.data),
        # Python automatically calls the @password.setter method.


    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    def can_purchase(self, item_obj):
        return self.budget >= item_obj.price
    def can_sell(self, item_obj):
        return item_obj in self.items


class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)   #must specify a column as primary key when creating models using flask
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=1024), nullable=False, unique=True)
    # #db.ForeignKey here connect the owner foreign key to the primary key 'id' in user table
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    def __repr__(self):
        return f'Item {self.name}'

    def buy(self, user):
        self.owner = user.id
        user.budget -= self.price
        db.session.commit()

    def sell(self, user):
        self.owner = None
        user.budget += self.price
        db.session.commit( )