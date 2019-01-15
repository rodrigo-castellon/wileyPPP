from flask import Flask


app = Flask(__name__)
app.config['SECRET_KEY'] = '1704f2e0ea194a113ff9d327aedb1da2f206d4dd'


from wileyapp import routes
