from datetime import datetime

from flask_login import UserMixin
from VisualNft import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class NFTItem(db.Model):
    __tablename__ = 'nft_item'
    id = db.Column(db.Integer, primary_key=True)
    media = db.Column(db.String(255))  # Store the media filename
    media_extension = db.Column(db.String(10))  # Store the media extension
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(255), nullable=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<NFTItem {self.name}>'



class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    @property
    def nft_items_count(self):
        return len(self.nft_items)

    def __repr__(self):
        return f'<Collection {self.name}>'

# ... (other models)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(255))
    lastname = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(255), nullable=True)
    profile_banner = db.Column(db.String(255))
    account_funds = db.Column(db.Float, default=0.0)

    
    nfts = db.relationship('NFTItem', backref='users', lazy=True)
    owned_collections = db.relationship('Collection', backref='users', lazy=True)
    user_notification = db.relationship('Notifications', backref='users')

class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # Add other relevant fields

    def __repr__(self):
        return f'<Activity {self.activity_type} by Users {self.user_id}>'