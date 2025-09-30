from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# This will be initialized in app.py
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    wishlists = db.relationship('Wishlist', backref='user', lazy=True)
    libraries = db.relationship('Library', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class GameCache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rawg_id = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    json_data = db.Column(db.Text, nullable=False)  # Store full JSON response
    thumbnail_url = db.Column(db.String(500))
    metacritic = db.Column(db.Integer)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    wishlists = db.relationship('Wishlist', backref='game', lazy=True)
    libraries = db.relationship('Library', backref='game', lazy=True)
    
    def __repr__(self):
        return f'<GameCache {self.title}>'

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    gamecache_id = db.Column(db.Integer, db.ForeignKey('game_cache.id'), nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Wishlist {self.user_id}:{self.gamecache_id}>'

class Library(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    gamecache_id = db.Column(db.Integer, db.ForeignKey('game_cache.id'), nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Library {self.user_id}:{self.gamecache_id}>'