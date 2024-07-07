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

def show_in_watchlist(show_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Watchlist WHERE ShowID = %s", (show_id,))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count > 0

def show_in_ratings(show_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Ratings WHERE ShowID = %s", (show_id,))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count > 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shows')
def shows():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM TVShows")
    shows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('shows.html', shows=shows)

@app.route('/watchlist')
def watchlist():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Watchlist INNER JOIN TVShows ON Watchlist.ShowID = TVShows.ShowID")
    watchlist = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('watchlist.html', watchlist=watchlist)

@app.route('/ratings')
def ratings():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Ratings INNER JOIN TVShows ON Ratings.ShowID = TVShows.ShowID")
    ratings = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('ratings.html', ratings=ratings)

@app.route('/all_tables')
def all_tables():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT s.ShowID, s.Title, s.Genre, s.Description, s.ReleaseDate, se.SeasonNumber, e.EpisodeNumber
    FROM TVShows s
    LEFT JOIN Seasons se ON s.ShowID = se.ShowID
    LEFT JOIN Episodes e ON se.SeasonID = e.SeasonID
    """
    cursor.execute(query)
    shows = cursor.fetchall()
    
    cursor.execute("SELECT * FROM Watchlist INNER JOIN TVShows ON Watchlist.ShowID = TVShows.ShowID")
    watchlist = cursor.fetchall()
    
    cursor.execute("SELECT * FROM Ratings INNER JOIN TVShows ON Ratings.ShowID = TVShows.ShowID")
    ratings = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('all_tables.html', shows=shows, watchlist=watchlist, ratings=ratings, 
                           show_in_watchlist=show_in_watchlist, show_in_ratings=show_in_ratings)

@app.route('/add_show', methods=['POST'])
def add_show():
    title = request.form['title']
    genre = request.form['genre']
    description = request.form['description']
    release_date = request.form['release_date']
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO TVShows (Title, Genre, Description, ReleaseDate) VALUES (%s, %s, %s, %s)",
                   (title, genre, description, release_date))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('shows'))

@app.route('/edit_show/<int:show_id>', methods=['GET', 'POST'])
def edit_show(show_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        description = request.form['description']
        release_date = request.form['release_date']
        cursor.execute("""
            UPDATE TVShows 
            SET Title=%s, Genre=%s, Description=%s, ReleaseDate=%s
            WHERE ShowID=%s
        """, (title, genre, description, release_date, show_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('shows'))
    else:
        cursor.execute("SELECT * FROM TVShows WHERE ShowID = %s", (show_id,))
        show = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('edit_show.html', show=show)

@app.route('/delete_show/<int:show_id>', methods=['POST'])
def delete_show(show_id):
    if not show_in_watchlist(show_id) and not show_in_ratings(show_id):
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM TVShows WHERE ShowID = %s", (show_id,))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('shows'))

@app.route('/add_watchlist', methods=['POST'])
def add_watchlist():
    show_id = request.form['show_id']
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Watchlist (ShowID) VALUES (%s)", (show_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('watchlist'))

@app.route('/delete_watchlist/<int:show_id>', methods=['POST'])
def delete_watchlist(show_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Watchlist WHERE ShowID = %s", (show_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('watchlist'))

@app.route('/add_rating', methods=['POST'])
def add_rating():
    user_id = request.form['user_id']
    show_id = request.form['show_id']
    rating = request.form['rating']
    review = request.form['review']
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Ratings (UserID, ShowID, Rating, Review) VALUES (%s, %s, %s, %s)", 
                   (user_id, show_id, rating, review))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('ratings'))

@app.route('/edit_rating/<int:rating_id>', methods=['GET', 'POST'])
def edit_rating(rating_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        rating = request.form['rating']
        review = request.form['review']
        cursor.execute("""
            UPDATE Ratings 
            SET Rating=%s, Review=%s 
            WHERE RatingID=%s
        """, (rating, review, rating_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('ratings'))
    else:
        cursor.execute("SELECT * FROM Ratings INNER JOIN TVShows ON Ratings.ShowID = TVShows.ShowID WHERE RatingID = %s", (rating_id,))
        rating = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('edit_rating.html', rating=rating)

@app.route('/delete_rating/<int:rating_id>', methods=['POST'])
def delete_rating(rating_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Ratings WHERE RatingID = %s", (rating_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('ratings'))

if __name__ == '__main__':
    app.run(debug=True)
