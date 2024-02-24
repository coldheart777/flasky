from flask_login import UserMixin
from flask import current_app
from itsdangerous import BadSignature

from . import login_manager
from . import db

from werkzeug.security import generate_password_hash, check_password_hash

from itsdangerous.url_safe import URLSafeTimedSerializer


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt=b'confirm')
        return s.dumps({'confirm': self.id})

    def confirm(self, token, out_time=3600):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt=b'confirm')
        try:
            data = s.loads(token, out_time)
        except BadSignature:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_token(self):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt=b'reset')
        return s.dumps({'reset': self.id})

    @staticmethod
    def reset_password(token, new_password, out_time=3600):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt=b'reset')
        try:
            data = s.loads(token, out_time)
        except BadSignature:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt=b'change_email')
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email})

    def change_email(self, token, out_time=3600):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt=b'change_email')
        try:
            data = s.loads(token, out_time)
        except BadSignature:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
