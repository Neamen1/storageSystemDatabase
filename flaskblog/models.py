from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    company = db.Column(db.String(120), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    # Define the relationship to Role via UserRoles
    roles = db.relationship('Roles', secondary='UserRoles', backref=db.backref('users', lazy='dynamic'))
    orders = db.relationship('Orders', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def has_roles(self, role):
        if isinstance(role, str):
            return role in (role.name for role in self.roles)
        else:
            return role in self.roles

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.company}')"


# Define the Role data-model
class Roles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = "UserRoles"
    userId = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    roleId = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    category = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantityInStock = db.Column(db.Integer, nullable=False)
    unitOfMeasure = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Product('{self.name}', '{self.category}', '{self.description}')"


class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    managerId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    maxCapacity = db.Column(db.Float, nullable=False)  # m^2
    currentCapacity = db.Column(db.Float, nullable=False)  # m^2
    storageCost = db.Column(db.Float, nullable=False)  # per m^2

    manager = db.relationship('User', backref='managed_warehouses')

    def __repr__(self):
        return f"Warehouse(id={self.id}, name={self.name}, location={self.location}, managerId={self.managerId}, maxCapacity={self.maxCapacity}, currentCapacity={self.currentCapacity}, storageCost={self.storageCost})"


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    orderedProducts = db.Column(db.JSON, nullable=False)
    totalAmount = db.Column(db.Float, nullable=False)
    orderStatus = db.Column(db.String(20), nullable=False)
    warehouseId = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False)
    orderDate = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Define relationships
    warehouse = db.relationship('Warehouse', backref='orders')

    def __repr__(self):
        return f"Order(id={self.id}, userId={self.userId}, orderStatus={self.orderStatus}, orderDate={self.orderDate})"


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
