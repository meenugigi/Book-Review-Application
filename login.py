import os
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, jsonify, request
from flask import Flask, render_template, redirect, session
from flask_session import Session
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

app.secret_key = "ayush"  

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')  
def home():  
    return render_template("home.html") 

#-----------------------------------------login-------------------------------
@app.route('/login')  
def login():  
    return render_template("login.html") 

#----------------------------------------register-----------------------------
@app.route('/register')  
def register():  
    return render_template("register.html") 

#--------------------------------------for registered users------------------
@app.route('/registered',methods = ["POST"])  
def registered():  
    firstname = request.form.get("fname")
    lastname = request.form.get("lname")
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    
    if db.execute("SELECT * FROM users WHERE username =:username",
        {"username": username}).rowcount != 0:
        return render_template("register.html", message ='This username is already taken!')    
    else: 
        db.execute("INSERT INTO users (firstname, lastname, username, password, email) VALUES (:firstname, :lastname, :username, :password, :email)",
                    {"firstname": firstname, "lastname": lastname, "username": username, "password": password, "email": email})   
        db.commit()
        return render_template("login.html", messages = 'Account created successfully!')  

#----------------------------------after successfull login------------------------- 
@app.route('/success',methods = ["GET" , "POST"])  
def success():  
    if request.method == "GET":  
        return render_template("login.html", display='Please login first')  
    else:
        log_username = request.form.get("log_username")
        log_password = request.form.get("log_password")
        if db.execute("select *from users where username=:username and password=:password", {"username": log_username, "password": log_password}).rowcount == 0:
                return render_template("error.html", message="Incorrect username/password!")
        elif request.method == "POST":  
                db.execute("INSERT INTO loggedusers (log_username, log_password) VALUES (:log_username, :log_password)",
                    {"log_username": log_username, "log_password": log_password})
                db.commit()
                session['email']=request.form['log_username']
                if 'email' in session: 
                    name = session['email']
                    return render_template('success.html', name=name)       
            
        else:
            return render_template("login.html")  

#-----------------------------------for logging out user---------------------------------
@app.route('/logout')  
def logout():  
    if 'email' in session:  
        session.pop('email',None)  
    return render_template('logout.html');  

#---------------------------------to search books---------------------------------------
@app.route('/searchbooks', methods = ["GET" , "POST"])  
def searchbooks():  
    if not session.get('email'):
        return render_template("login.html", display='Please login first') 
    name = session['email']
    return render_template("searchbooks.html", name=name) 
            
#---------------------------------displays list of books searched for--------------------
@app.route('/books',methods = ["GET" , "POST"])  
def books(): 
    if request.method == "GET":  
        return render_template("login.html", display='Please login first')  
    else:
        books = db.execute("SELECT id, isbn, title, author, year FROM books").fetchall()
        fetch_id = request.form.get("id")
        fetch_isbn = request.form.get("isbn")
        fetch_title = request.form.get("title")
        fetch_author = request.form.get("author")
    
        book_isbn = fetch_isbn
        book_title = fetch_title
        book_author= fetch_author
        name = session['email']
        if db.execute("SELECT id, isbn, title, author, year FROM books WHERE isbn LIKE :isbn AND title LIKE :title AND author LIKE :author" , 
                        {"isbn": f"%{book_isbn}%" , "title": f"%{book_title}%" , "author": f"%{book_author}%"}).rowcount == 0:
            return render_template("error.html", message="Book not Found!")
        else:
            book = db.execute("SELECT id, isbn, title, author, year FROM books WHERE isbn LIKE :isbn AND title LIKE :title AND author LIKE :author" , 
                        {"isbn": f"%{book_isbn}%" , "title": f"%{book_title}%" , "author": f"%{book_author}%"}).fetchall()
            return render_template("books.html", book=book, name=name)

#-----------------------------------------displays data of a selected boook----------------------    
@app.route("/bookpage/<book_isbn>", methods = ["GET" , "POST"])  
def bookpage(book_isbn): 
    #if request.method == "GET":  
     #   return render_template("login.html", display='Please login first')  
    #else:
    bookpages = db.execute("SELECT id, isbn, title, author, year FROM books WHERE isbn = :isbn" , 
                        {"isbn": book_isbn})
   
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "jSZkT1XWjiI3KuEUsdK7g", "isbns": book_isbn})
    if res.status_code == 200:
        receive=res.json()
    
        reviewscount=receive["books"][0]["reviews_count"]
        avgrating=receive["books"][0]["average_rating"]
    else:
        displays = 'No reviews found'  
        
    name = session['email'] 
    username = session['email']
    isbn = book_isbn
    bookpages01 = bookpages
    if db.execute("SELECT username, isbn, ratings FROM ratings WHERE username = :username AND isbn = :isbn",
        {"username": session['email'] , "isbn": book_isbn}).rowcount != 0:

        yourrating = db.execute("SELECT username, isbn, ratings, reviews FROM ratings WHERE username = :username AND isbn = :isbn", {"username": session['email'] , "isbn": book_isbn})
        return render_template("bookpage.html", bookpages01 = bookpages01, yourrating = yourrating, reviewscount = reviewscount,  avgrating= avgrating, name=name) 
             
    else:
        return render_template("bookpage.html", bookpages=bookpages, reviewscount = reviewscount,  avgrating= avgrating, name=name) 

#----------------------------------------------API access------------------------------------------------
@app.route("/api/books/<book_isbn>")
def book_api(book_isbn):

    if db.execute("SELECT id, isbn, title, author, year FROM books WHERE isbn = :isbn" , {"isbn": book_isbn}).rowcount == 0:
         return jsonify({"error 404": "Book not found"}), 404

    else:
        bookapi = db.execute("SELECT id, isbn, title, author, year FROM books WHERE isbn = :isbn" , {"isbn": book_isbn})
    names = []
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "jSZkT1XWjiI3KuEUsdK7g", "isbns": book_isbn})
    if res.status_code == 200:
        receive=res.json()
    
        reviewscount=receive["books"][0]["reviews_count"]
        avgrating=receive["books"][0]["average_rating"]
    for bookapi in bookapi:
       
        return jsonify({
            "book isbn": bookapi.isbn,
            "book title": bookapi.title,
            "book author": bookapi.author,
            "year": bookapi.year,
            "average_score": avgrating,
            "review_count": reviewscount
        })

#---------------------------------------allowing user to submit book reviews----------------------------
@app.route("/reviewsubmit/<book_isbn>", methods = ["GET", "POST"])
def reviewsubmit(book_isbn):
    #if request.method == "POST":
    if request.method == "GET":  
        return render_template("login.html", display='Please login first')  
    else:
        username = session['email']
        isbn=book_isbn
        reviews = request.form.get("reviews")
        ratings = request.form.get("ratings")

        db.execute("INSERT INTO ratings (username, isbn, ratings, reviews) VALUES (:username, :isbn, :ratings, :reviews )",
                    {"username": username, "isbn": book_isbn, "ratings": ratings, "reviews": reviews})
        db.commit()
        return render_template("reviewsubmit.html")  
      
if __name__ == '__main__':  
    app.run(debug = True)  
