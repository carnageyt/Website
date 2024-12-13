from flask import Flask, request, render_template, redirect, session, url_for
import os
import sqlite3

# Set up Flask app
myapp = Flask(__name__)
myapp.secret_key = "6f2e82f42ac12559a51b8f9d1e3be9e93a5433d2d7b3b710ed5f3d9537f4bb92"  # Secret key for session management

# Get the current file's directory
currentlocation = os.path.dirname(os.path.abspath(__file__))

# Initialize the database
def init_db():
    with sqlite3.connect(os.path.join(currentlocation, "WebsiteDatabase.db")) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL UNIQUE,
                            password TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS movies (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            genre TEXT NOT NULL,
                            rating REAL NOT NULL)''')
        conn.commit()

init_db()

# Route for the homepage to display all movies
@myapp.route("/", methods=["GET"])
def homepage():
    if "username" not in session:  # Check if the user is logged in
        return redirect("/login")  # Redirect to login page if not logged in

    movies = []  # Initialize an empty list for movies
    try:
        # Connect to the database
        sqlconnection = sqlite3.connect(os.path.join(currentlocation, "WebsiteDatabase.db"))
        cursor = sqlconnection.cursor()

        # Fetch all movies from the database
        query = "SELECT id, title, genre, rating FROM movies"
        cursor.execute(query)
        movies = cursor.fetchall()  # Fetch all movies
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        sqlconnection.close()
    
    # Pass movies to the template
    return render_template("homepage.html", movies=movies)

# Route for the login page
@myapp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get username and password from the form
        UN = request.form["username"]
        PW = request.form["password"]

        try:
            # Connect to the database
            sqlconnection = sqlite3.connect(os.path.join(currentlocation, "WebsiteDatabase.db"))
            cursor = sqlconnection.cursor()

            # Use a parameterized query for login check
            query1 = "SELECT username, password FROM users WHERE username = ? AND password = ?"
            cursor.execute(query1, (UN, PW))
            rows = cursor.fetchall()

            if len(rows) == 1:
                # Save the user's login in the session
                session["username"] = UN
                return redirect("/")
            else:
                return "Invalid username or password. <a href='/login'>Try again</a>"
        except Exception as e:
            return f"An error occurred: {e}"
        finally:
            sqlconnection.close()
    return render_template("login.html")

# Add a logout route
@myapp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Route for the registration page
@myapp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        UN = request.form["username"]
        PW = request.form["password"]

        try:
            # Connect to the database
            sqlconnection = sqlite3.connect(os.path.join(currentlocation, "WebsiteDatabase.db"))
            cursor = sqlconnection.cursor()

            # Insert the new user into the database
            query = "INSERT INTO users (username, password) VALUES (?, ?)"
            cursor.execute(query, (UN, PW))
            sqlconnection.commit()
            return redirect("/login")
        except Exception as e:
            return f"An error occurred: {e}"
        finally:
            sqlconnection.close()
    return render_template("register.html")

# Route to add a new movie
@myapp.route("/add_movie", methods=["GET", "POST"])
def add_movie():
    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        genre = request.form["genre"]
        rating = request.form["rating"]

        try:
            sqlconnection = sqlite3.connect(os.path.join(currentlocation, "WebsiteDatabase.db"))
            cursor = sqlconnection.cursor()
            query = "INSERT INTO movies (title, genre, rating) VALUES (?, ?, ?)"
            cursor.execute(query, (title, genre, rating))
            sqlconnection.commit()
            return redirect("/")
        except Exception as e:
            return f"An error occurred: {e}"
        finally:
            sqlconnection.close()
    return render_template("add_movie.html")

# Route to edit a movie
@myapp.route("/edit_movie/<int:id>", methods=["GET", "POST"])
def edit_movie(id):
    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        genre = request.form["genre"]
        rating = request.form["rating"]

        try:
            sqlconnection = sqlite3.connect(os.path.join(currentlocation, "WebsiteDatabase.db"))
            cursor = sqlconnection.cursor()
            query = "UPDATE movies SET title = ?, genre = ?, rating = ? WHERE id = ?"
            cursor.execute(query, (title, genre, rating, id))
            sqlconnection.commit()
            return redirect("/")
        except Exception as e:
            return f"An error occurred: {e}"
        finally:
            sqlconnection.close()
    else:
        try:
            sqlconnection = sqlite3.connect(os.path.join(currentlocation, "WebsiteDatabase.db"))
            cursor = sqlconnection.cursor()
            query = "SELECT title, genre, rating FROM movies WHERE id = ?"
            cursor.execute(query, (id,))
            movie = cursor.fetchone()
            return render_template("edit_movie.html", movie=movie)
        except Exception as e:
            return f"An error occurred: {e}"
        finally:
            sqlconnection.close()

# Route to delete a movie
@myapp.route("/delete_movie/<int:id>", methods=["GET"])
def delete_movie(id):
    if "username" not in session:
        return redirect("/login")

    try:
        sqlconnection = sqlite3.connect(os.path.join(currentlocation, "WebsiteDatabase.db"))
        cursor = sqlconnection.cursor()
        query = "DELETE FROM movies WHERE id = ?"
        cursor.execute(query, (id,))
        sqlconnection.commit()
        return redirect("/")
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        sqlconnection.close()

if __name__ == "__main__":
    myapp.run(debug=True)