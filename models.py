from app import db

# moving models to seperate file to keep items seperate

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    #insert 'genres' column
    genres = db.Column(db.String(), nullable=False)
    image_link = db.Column(db.String(240))
    facebook_link = db.Column(db.String(120))

      #Add a seeking_talent(bool) and seeking_description. 
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
      #should have a relationship with shows(to pull artists who are playing there)
    shows = db.relationship('Show', backref="venue", lazy=True)
    
    def __repr__(self):
        return '<Venue {}>'.format(self.name)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate -done

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

      #create a seeking_venue(bool) and seeking_description
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
      #create relationship with Show model (to show all the shows they are playing and at which venue)
    shows = db.relationship('Show', backref='artist', lazy=True)
    
    def __repr__(self):
        return '<Artist {}>'.format(self.name)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate -done

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. -done


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Show {}{}>'.format(self.artist_id, self.venue_id)


    