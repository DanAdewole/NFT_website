from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_login import LoginManager
from flask_migrate import Migrate
import os

os.environ['FLASK_APP'] = 'VisualNft'

app = Flask(__name__)
UPLOAD_FOLDER = 'VisualNft/static/images/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SECRET_KEY'] = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/nftdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view="login"
login_manager.login_message_category="info"

from VisualNft import routes