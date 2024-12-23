import datetime
from flask_login import UserMixin
from .extensions import db, login_manager

@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=0)
    commission_rate = db.Column(db.Numeric(10, 2), default=0)
    webhook_url = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(50), default="user")
    usdt_wallet = db.Column(db.String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<Пользователь #{self.id} {self.username}, роль={self.role}>"

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    commission = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status = db.Column(db.String(50), default="pending")  # pending, confirmed, canceled, expired
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship("User", backref=db.backref("transactions", lazy=True))

    def __repr__(self) -> str:
        return f"<Транзакция #{self.id}, статус={self.status}>"
