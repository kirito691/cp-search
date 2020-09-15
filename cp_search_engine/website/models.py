from datetime import datetime
from hashlib import md5
from time import time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from website import app, db, login

marked = db.Table(
	'marked',
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('problem_id', db.Integer, db.ForeignKey('problem.id'))
)

class Problem(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	problem_name = db.Column(db.String(64), index=True)
	problem_link = db.Column(db.String(64), index=True, unique=True)
	keywords = db.Column(db.String(140), index=True)


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))

	marked_problems = db.relationship(
		'Problem', secondary=marked,
		primaryjoin=(marked.c.user_id==id),
		secondaryjoin="marked.c.problem_id==Problem.id",
		backref=db.backref('markers', lazy='dynamic'), lazy='dynamic')

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
			digest, size)

	def get_reset_password_token(self, expires_in=600):
		return jwt.encode(
			{'reset_password': self.id, 'exp': time() + expires_in},
			app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

	def is_marked(self, problem):
		return self.marked_problems.filter()


	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, app.config['SECRET_KEY'],
							algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(id)


@login.user_loader
def load_user(id):
	return User.query.get(int(id))