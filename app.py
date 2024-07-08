from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database configuration
db_config = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost',
    'database': 'tv_show_tracker'
}

# Function to fetch subscriptions
def fetch_subscriptions():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Subscription")
    subscriptions = cursor.fetchall()
    cursor.close()
    conn.close()
    return subscriptions

# Route for subscriptions page
@app.route('/subscriptions')
def subscriptions():
    subscriptions = fetch_subscriptions()
    return render_template('subscriptions.html', subscriptions=subscriptions)

# Route for editing a subscription
@app.route('/edit_subscription/<int:user_id>', methods=['GET', 'POST'])
def edit_subscription(user_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        payment_status = request.form['payment_status']
        cursor.execute("""
            UPDATE Subscription 
            SET PaymentStatus = %s 
            WHERE UserID = %s
        """, (payment_status, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('subscriptions'))
    else:
        cursor.execute("SELECT * FROM Subscription WHERE UserID = %s", (user_id,))
        subscription = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('edit_subscription.html', subscription=subscription)

# Function to check if a show is in the watchlist
def show_in_watchlist(show_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Watchlist WHERE ShowID = %s", (show_id,))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count > 0

# Function to check if a show has ratings
def show_in_ratings(show_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Ratings WHERE ShowID = %s", (show_id,))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count > 0

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for displaying all shows
@app.route('/shows')
def shows():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM TVShows")
    shows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('shows.html', shows=shows)

# Route for adding a new show
@app.route('/add_show', methods=['POST'])
def add_show():
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        description = request.form['description']
        release_date = request.form['release_date']
        time = request.form['time']
        season_number = request.form['season_number']
        episode_number = request.form['episode_number']
        episode_title = request.form['episode_title']
        air_date = request.form['air_date']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        try:
            # Insert into TVShows table
            cursor.execute("""
                INSERT INTO TVShows (Title, Genre, Description, ReleaseDate, Timing)
                VALUES (%s, %s, %s, %s, %s)
            """, (title, genre, description, release_date, time))
            conn.commit()

            # Retrieve the auto-generated ShowID
            show_id = cursor.lastrowid

            # Insert into Seasons table
            cursor.execute("""
                INSERT INTO Seasons (ShowID, SeasonNumber)
                VALUES (%s, %s)
            """, (show_id, season_number))
            conn.commit()

            # Retrieve the auto-generated SeasonID
            season_id = cursor.lastrowid

            # Insert into Episodes table
            cursor.execute("""
                INSERT INTO Episodes (SeasonID, EpisodeNumber, Title, AirDate)
                VALUES (%s, %s, %s, %s)
            """, (season_id, episode_number, episode_title, air_date))
            conn.commit()

            cursor.close()
            conn.close()

            return redirect(url_for('shows'))

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            cursor.close()
            conn.close()
            # Handle error appropriately, e.g., show an error page
            return "Error occurred while adding the show. Please try again."

# Route for displaying and managing the watchlist
@app.route('/watchlist', methods=['GET', 'POST'])
def watchlist():
    if request.method == 'POST':
        show_id = request.form['show_id']
        user_id = request.form['user_id']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Watchlist (UserID, ShowID) VALUES (%s, %s)", (user_id, show_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('watchlist'))
    
    else:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Watchlist INNER JOIN TVShows ON Watchlist.ShowID = TVShows.ShowID")
        watchlist = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template('watchlist.html', watchlist=watchlist)

# Route for displaying all ratings
@app.route('/ratings')
def ratings():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Ratings INNER JOIN TVShows ON Ratings.ShowID = TVShows.ShowID")
    ratings = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('ratings.html', ratings=ratings)

# Route for adding a new rating
@app.route('/add_rating', methods=['POST'])
def add_rating():
    if request.method == 'POST':
        user_id = request.form['user_id']
        show_id = request.form['show_id']
        rating = request.form['rating']
        review = request.form['review']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Ratings (UserID, ShowID, Rating, Review)
            VALUES (%s, %s, %s, %s)
        """, (user_id, show_id, rating, review))
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('ratings'))

# Route for displaying all tables
@app.route('/all_tables')
def all_tables():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    # Fetch all shows with their seasons and episodes
    query = """
    SELECT s.ShowID, s.Title, s.Genre, s.Description, s.ReleaseDate, se.SeasonNumber, e.EpisodeNumber
    FROM TVShows s
    LEFT JOIN Seasons se ON s.ShowID = se.ShowID
    LEFT JOIN Episodes e ON se.SeasonID = e.SeasonID
    """
    cursor.execute(query)
    shows = cursor.fetchall()
    
    # Fetch shows in the watchlist
    cursor.execute("SELECT TVShows.ShowID, TVShows.Title, TVShows.Genre, TVShows.Description, TVShows.ReleaseDate FROM Watchlist INNER JOIN TVShows ON Watchlist.ShowID = TVShows.ShowID")
    watchlist = cursor.fetchall()
    
    # Fetch ratings for shows
    cursor.execute("SELECT Ratings.RatingID, TVShows.ShowID, TVShows.Title, Ratings.UserID, Ratings.Rating, Ratings.Review FROM Ratings INNER JOIN TVShows ON Ratings.ShowID = TVShows.ShowID")
    ratings = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('all_tables.html', shows=shows, watchlist=watchlist, ratings=ratings)

# Route for editing a show in the watchlist
@app.route('/edit_watchlist/<int:show_id>', methods=['GET', 'POST'])
def edit_watchlist(show_id):
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        description = request.form['description']
        release_date = request.form['release_date']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE TVShows 
            SET Title = %s, Genre = %s, Description = %s, ReleaseDate = %s 
            WHERE ShowID = %s
        """, (title, genre, description, release_date, show_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('watchlist'))
    else:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT TVShows.ShowID, TVShows.Title, TVShows.Genre, TVShows.Description, TVShows.ReleaseDate 
            FROM Watchlist 
            INNER JOIN TVShows ON Watchlist.ShowID = TVShows.ShowID 
            WHERE TVShows.ShowID = %s
        """, (show_id,))
        watchlist = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('edit_watchlist.html', watchlist=watchlist)

# Route for editing a rating
@app.route('/edit_rating/<int:rating_id>', methods=['GET', 'POST'])
def edit_rating(rating_id):
    if request.method == 'POST':
        rating = request.form['rating']
        review = request.form['review']
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("UPDATE Ratings SET Rating = %s, Review = %s WHERE RatingID = %s", (rating, review, rating_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('ratings'))
    else:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Ratings WHERE RatingID = %s", (rating_id,))
        rating = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('edit_rating.html', rating=rating)

# Route for deleting a show from the watchlist
@app.route('/delete_watchlist/<int:show_id>', methods=['POST'])
def delete_watchlist(show_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Watchlist WHERE ShowID = %s", (show_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('watchlist'))

# Route for deleting a rating
@app.route('/delete_rating/<int:rating_id>', methods=['POST'])
def delete_rating(rating_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Ratings WHERE RatingID = %s", (rating_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('ratings'))

@app.route('/tvshows')
def tvshows():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM TVShows")
    tvshows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('tvshows.html', tvshows=tvshows)


if __name__ == '__main__':
    app.run(debug=True)
