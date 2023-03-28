from app import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from os import getenv

app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)