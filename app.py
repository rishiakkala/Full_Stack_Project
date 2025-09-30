from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
from datetime import datetime
import json

# Import models
from models import db, User, GameCache, Wishlist, Library

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'matrixrealm_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///matrixrealm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

# RAWG API configuration
RAWG_API_KEY = "62df77eb3a5d4b6bb60d4da27f735c56"  # Replace with your actual API key
RAWG_BASE_URL = "https://api.rawg.io/api"

# Helper function to fetch data from RAWG API
def fetch_from_rawg(endpoint, params=None):
    if params is None:
        params = {}
    params['key'] = RAWG_API_KEY
    
    url = f"{RAWG_BASE_URL}/{endpoint}"
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Routes
@app.route('/')
def home():
    # Fetch trending and top games
    trending_games = fetch_from_rawg('games', {'ordering': '-added', 'page_size': 10})
    top_games = fetch_from_rawg('games', {'ordering': '-rating', 'page_size': 10})
    genres = fetch_from_rawg('genres', {'page_size': 10})
    
    return render_template('home.html', 
                          trending_games=trending_games.get('results', []) if trending_games else [],
                          top_games=top_games.get('results', []) if top_games else [],
                          genres=genres.get('results', []) if genres else [])

@app.route('/catalog')
def catalog():
    genre_id = request.args.get('genre', None)
    page = request.args.get('page', 1, type=int)
    
    params = {'page': page, 'page_size': 20}
    if genre_id:
        params['genres'] = genre_id
    
    games = fetch_from_rawg('games', params)
    
    return render_template('catalog.html', 
                          games=games.get('results', []) if games else [],
                          next_page=games.get('next') if games else None,
                          prev_page=games.get('previous') if games else None)

@app.route('/game/<int:game_id>')
def game_detail(game_id):
    # Check if game exists in cache
    game_cache = GameCache.query.filter_by(rawg_id=game_id).first()
    
    if game_cache and (datetime.now() - game_cache.last_updated).days < 7:
        # Use cached data if less than a week old
        game_data = json.loads(game_cache.json_data)
    else:
        # Fetch fresh data from API
        game_data = fetch_from_rawg(f'games/{game_id}')
        
        if game_data:
            # Cache the data
            if game_cache:
                game_cache.json_data = json.dumps(game_data)
                game_cache.last_updated = datetime.now()
            else:
                new_cache = GameCache(
                    rawg_id=game_id,
                    title=game_data.get('name', ''),
                    slug=game_data.get('slug', ''),
                    json_data=json.dumps(game_data),
                    thumbnail_url=game_data.get('background_image', ''),
                    metacritic=game_data.get('metacritic')
                )
                db.session.add(new_cache)
            
            db.session.commit()
    
    # Get related games (same series)
    related_games = fetch_from_rawg(f'games/{game_id}/game-series')
    
    # Check if game is in user's wishlist or library
    in_wishlist = False
    in_library = False
    
    if 'user_id' in session:
        user_id = session['user_id']
        wishlist_item = Wishlist.query.filter_by(user_id=user_id, gamecache_id=game_id).first()
        library_item = Library.query.filter_by(user_id=user_id, gamecache_id=game_id).first()
        
        in_wishlist = wishlist_item is not None
        in_library = library_item is not None
    
    return render_template('game_detail.html', 
                          game=game_data,
                          related_games=related_games.get('results', []) if related_games else [],
                          in_wishlist=in_wishlist,
                          in_library=in_library)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@app.route('/wishlist')
def wishlist():
    if 'user_id' not in session:
        flash('Please log in to view your wishlist', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    wishlist_items = Wishlist.query.filter_by(user_id=user_id).all()
    
    games = []
    for item in wishlist_items:
        game_cache = GameCache.query.filter_by(id=item.gamecache_id).first()
        if game_cache:
            game_data = json.loads(game_cache.json_data)
            games.append(game_data)
    
    return render_template('wishlist.html', games=games)

@app.route('/wishlist/toggle', methods=['POST'])
def toggle_wishlist():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'}), 401
    
    data = request.get_json()
    game_id = data.get('game_id')
    user_id = session['user_id']
    
    # Check if game exists in cache
    game_cache = GameCache.query.filter_by(rawg_id=game_id).first()
    
    if not game_cache:
        # Fetch and cache game data
        game_data = fetch_from_rawg(f'games/{game_id}')
        
        if not game_data:
            return jsonify({'success': False, 'message': 'Game not found'}), 404
        
        game_cache = GameCache(
            rawg_id=game_id,
            title=game_data.get('name', ''),
            slug=game_data.get('slug', ''),
            json_data=json.dumps(game_data),
            thumbnail_url=game_data.get('background_image', ''),
            metacritic=game_data.get('metacritic')
        )
        db.session.add(game_cache)
        db.session.commit()
    
    # Check if game is already in wishlist
    wishlist_item = Wishlist.query.filter_by(user_id=user_id, gamecache_id=game_cache.id).first()
    
    if wishlist_item:
        # Remove from wishlist
        db.session.delete(wishlist_item)
        db.session.commit()
        return jsonify({'success': True, 'in_wishlist': False})
    else:
        # Add to wishlist
        new_wishlist_item = Wishlist(user_id=user_id, gamecache_id=game_cache.id)
        db.session.add(new_wishlist_item)
        db.session.commit()
        return jsonify({'success': True, 'in_wishlist': True})

@app.route('/library')
def library():
    if 'user_id' not in session:
        flash('Please log in to view your library', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    library_items = Library.query.filter_by(user_id=user_id).all()
    
    games = []
    for item in library_items:
        game_cache = GameCache.query.filter_by(id=item.gamecache_id).first()
        if game_cache:
            game_data = json.loads(game_cache.json_data)
            games.append(game_data)
    
    return render_template('library.html', games=games)

@app.route('/library/add', methods=['POST'])
def add_to_library():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'}), 401
    
    data = request.get_json()
    game_id = data.get('game_id')
    user_id = session['user_id']
    
    # Check if game exists in cache
    game_cache = GameCache.query.filter_by(rawg_id=game_id).first()
    
    if not game_cache:
        # Fetch and cache game data
        game_data = fetch_from_rawg(f'games/{game_id}')
        
        if not game_data:
            return jsonify({'success': False, 'message': 'Game not found'}), 404
        
        game_cache = GameCache(
            rawg_id=game_id,
            title=game_data.get('name', ''),
            slug=game_data.get('slug', ''),
            json_data=json.dumps(game_data),
            thumbnail_url=game_data.get('background_image', ''),
            metacritic=game_data.get('metacritic')
        )
        db.session.add(game_cache)
        db.session.commit()
    
    # Check if game is already in library
    library_item = Library.query.filter_by(user_id=user_id, gamecache_id=game_cache.id).first()
    
    if library_item:
        return jsonify({'success': False, 'message': 'Game already in library'})
    else:
        # Add to library
        new_library_item = Library(user_id=user_id, gamecache_id=game_cache.id)
        db.session.add(new_library_item)
        db.session.commit()
        return jsonify({'success': True})

@app.route('/search')
def search():
    query = request.args.get('q', '')
    genre = request.args.get('genre', '')
    platform = request.args.get('platform', '')
    ordering = request.args.get('ordering', '-relevance')
    
    if not query:
        return render_template('search.html', games=[], query='')
    
    # Prepare search parameters
    params = {
        'search': query,
        'page_size': 20,
        'ordering': ordering
    }
    
    # Add filters if provided
    if genre:
        params['genres'] = genre
    if platform:
        params['platforms'] = platform
    
    # Fetch genres and platforms for filter dropdowns
    genres = fetch_from_rawg('genres', {'page_size': 20})
    platforms = fetch_from_rawg('platforms', {'page_size': 20})
    
    # Fetch search results with filters
    search_results = fetch_from_rawg('games', params)
    
    return render_template('search.html', 
                          games=search_results.get('results', []) if search_results else [],
                          query=query,
                          selected_genre=genre,
                          selected_platform=platform,
                          selected_ordering=ordering,
                          genres=genres.get('results', []) if genres else [],
                          platforms=platforms.get('results', []) if platforms else [])

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in to view your profile', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    wishlist_count = Wishlist.query.filter_by(user_id=user_id).count()
    library_count = Library.query.filter_by(user_id=user_id).count()
    
    return render_template('profile.html', 
                          user=user,
                          wishlist_count=wishlist_count,
                          library_count=library_count)

# Create database tables before first request
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)