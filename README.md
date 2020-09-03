set DATABASE_URL=postgres://fizarurozyjpdp:7d84df8f2660dda8f5a012db32a541fada530f2c0f02ca6cb1beb603145cf5f8@ec2-52-70-15-120.compute-1.amazonaws.com:5432/dcbkb030jbnk8c



This is a book search (flask) application with the following features
- register
- login (gor registered users only)
- search books
- view details of a particular book
- get goodreads data of a specific book using goodreads API
- provide API access to the application
- allow users to rate and review the book
- preventing same user to rate the same book twice
- import books.csv file to the database

login.py ---> this file contains the python code to run the application
import.py ---> this file contains the python code to export the details about 5000 books to the database.

bookpage.html ---> contains html code to display details about a specific book which includes goodreads data and also allowing users to rate and review the book.

books.html ---> contains html code to display the list of matching search reults when user inputs serach data to search for a book.

error.html ---> contains html code to display any sort of validation messages.

home.html ---> contains html code that displays the home page i.e first page that appears on running the flask application.

login.html ---> contains html code for permitting registered users to login. Throws a validation if users inputs incorrects username/password.

logout.html ---> contains html code for the logout page.

register.html ---> contains html code for allowing users to register. The application does not allow to create duplicate usernames.

reviewsubmit.html ---> contains html code to display page that appears on successfully submitting a rating and review for a specific book.

searchbooks.html ---> contains html code that permits users to search for a book. The application can search for books even if the user enters only partial search data.

success.html ---> contains html code for page that appears on succesful login to the application.

Project Demo Link: https://youtu.be/g1mOF-fYXgY
