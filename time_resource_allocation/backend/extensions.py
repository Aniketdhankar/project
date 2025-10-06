"""
Flask Extensions
Centralized initialization of Flask extensions
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
