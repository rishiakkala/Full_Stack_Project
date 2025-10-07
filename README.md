# MatrixRealm - Video Game Showcase

MatrixRealm is a full-stack web application that serves as a video game discovery and showcase platform, similar to RAWG.io. Users can browse games, view detailed information, create accounts, save games to their wishlist or library, and search by genre or title.

## Features

- **Home Page**: Displays trending games, top-rated games, and browse by genre sections
- **User Authentication**: Register, login, and logout functionality
- **Game Details**: View comprehensive information about each game
- **Wishlist & Library**: Save games to your personal collection
- **Search & Filter**: Find games by title or filter by genre
- **Profile Page**: View your account information and collection stats

## Tech Stack

- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Interactivity**: JavaScript
- **Backend**: Flask (Python)
- **Database**: SQLite
- **API Integration**: RAWG Video Games Database API

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- RAWG API key (get one at [https://rawg.io/apidocs](https://rawg.io/apidocs))

### Installation

1. Clone the repository or download the source code

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the project root with your RAWG API key:
   ```
   RAWG_API_KEY=your_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

6. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

7. Run the application:
   ```
   flask run
   ```

8. Open your browser and navigate to `http://127.0.0.1:5000/`

## Project Structure

```
MatrixRealm/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── static/                # Static files
│   ├── css/               # CSS stylesheets
│   │   └── style.css      # Main stylesheet
│   └── js/                # JavaScript files
│       └── main.js        # Main JavaScript file
├── templates/             # HTML templates
│   ├── base.html          # Base template with common elements
│   ├── home.html          # Home page
│   ├── game_detail.html   # Game details page
│   ├── catalog.html       # Game catalog/browse page
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── wishlist.html      # User's wishlist
│   ├── library.html       # User's library
│   ├── profile.html       # User profile page
│   └── search.html        # Search results page
└── requirements.txt       # Python dependencies
```

## API Integration

The application uses the RAWG Video Games Database API to fetch game data. The API responses are cached in the local SQLite database to reduce API calls and improve performance.

## Demo

### Home Page
The home page displays trending games, top-rated games, and allows browsing by genre.

![Home Page Screenshot](static/img/home1.png)

### User Registration
New users can create an account to save games to their wishlist and library.

![Registration Page Screenshot](static/img/screenshots/register.png)

### Game Details
View comprehensive information about each game including description, platforms, ratings, and more.

![Game Details Screenshot](static/img/screenshots/game_detail.png)

### Search and Filter
Search for games by title and filter results by genre, platform, and other criteria.

![Search Results Screenshot](static/img/screenshots/search.png)

### Wishlist
Save games to your wishlist for future reference.

![Wishlist Screenshot](static/img/screenshots/wishlist.png)

### Library
Add games you own to your personal library.

![Library Screenshot](static/img/screenshots/library.png)

### User Profile
View your account information and collection statistics.

![Profile Screenshot](static/img/screenshots/profile.png)

