from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import secret_key, sql_username, sql_pass


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + sql_username + ':' + sql_pass + '@localhost:8889/hockey_ticker'
app.config['SQLALCHEMY_ECHO'] = False
db = SQLAlchemy(app)
app.secret_key = secret_key