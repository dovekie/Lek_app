"""Models and database functions """

from flask_sqlalchemy import SQLAlchemy
import os
# from flask.ext.login import LoginManager, UserMixin # the last two are intended to make oauth work

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of the birdwatch website"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    twitter_name = db.Column(db.String(100), nullable=False, unique=True)
    twitter_id = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(100), nullable=True)
    auth_token = db.Column(db.String(100), nullable=False)
    auth_secret = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(64), nullable=True, unique=True)
    bird_count = db.Column(db.Integer, nullable=True)

    #location = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """Provide helpful information representation when printed!"""

        return "<User user_id = %s email = %s username = %s>" %(self.user_id, self.email, self.username)


class Bird(db.Model):
    """Birds from eBird"""

    __tablename__ = "birds"

    taxon_id = db.Column(db.Text, primary_key=True)
    common_name = db.Column(db.Text, nullable=True)
    sci_name = db.Column(db.Text, nullable=False)
    sp_species = db.Column(db.Text, nullable=False)
    sp_genus = db.Column(db.Text, nullable=False) 
    sp_family = db.Column(db.Text, nullable=False)
    sp_order = db.Column(db.Text, nullable=False)
    
    #location data follows. Some of these beeps might not have any!
    region = db.Column(db.Text, nullable=True)
    subregion = db.Column(db.Text, nullable=True)
    nonbreeding_region = db.Column(db.Text, nullable=True)


    def __repr__(self):
        """Provide helpful information representation when printed!"""

        return "<TaxonID = %s species = %s>" %(self.taxon_id, self.sci_name)

class Observation(db.Model):
    """User observations"""

    __tablename__ = "observations"

    obs_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    bird_id = db.Column(db.Text, db.ForeignKey('birds.taxon_id'), nullable=False)
    obs_timestamp = db.Column(db.Integer, nullable=False)

    # Define relationship to users
    user = db.relationship("User", backref=db.backref("observations", order_by=Bird.taxon_id))

    # Define relationship to birds
    bird = db.relationship("Bird", backref=db.backref("observations", order_by=Bird.taxon_id))

    def __repr__(self):
        """Provide helpful information representation when printed!"""

        return "<Observation user_id = %s taxon_id = %s>" %(self.user_id, self.bird_id)

class UserSearch(db.Model):
    """Saved user searches"""

    __tablename__ = "usersearches"

    search_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    search_string = db.Column(db.LargeBinary, nullable=False)
    user_default = db.Column(db.Boolean, nullable=False, default=False)
    search_timestamp = db.Column(db.Integer, nullable=False)

    # Define relationship with users
    user = db.relationship("User", backref=db.backref("usersearches", order_by=User.user_id))

    def __repr__(self):
        """Provide helpful information when printed!"""

        return "<Search user_id = %s search_string = %s>" %(self.user_id, self.search_string)

##############################################################################
# Helper functions
# import login string

# try:
db_login = os.environ.get('BIRDWATCH_DB_URL')
# except KeyError:
#     from sos import db_login


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_login
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app 
    connect_to_db(app)
    print "Connected to DB."