#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

#Instantiate a Migrate object
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database - done

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models import *


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue. - Done

  # write a query that selects all venue
    all_venues = (
        Venue.query.with_entities(Venue.city, Venue.state)
        .group_by(Venue.city, Venue.state)
        .all()
    )

    data = []
    # display all venues by city/state and name only. Call 'area' per venues. -html -Done
    for area in all_venues:
        venues_in_city = (
            Venue.query.filter(Venue.city == area[0])
            .filter(Venue.state == area[1])
            .all()
        )
        data.append({"city": area.city, "state": area.state, "venues": venues_in_city})

      # removed dummy code for neatness

    return render_template('pages/venues.html', areas=data);

#  Search Venue
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. -Done

  #write a search query using ilike() operator. 
  search_term = request.form.get('search_term', '')
  venues = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
  data = []

  for venue in venues:
      num_upcoming_shows = 0
      shows = db.session.query(Show).filter(Show.venue_id == venue.id)
      for show in shows:
          if (show.start_time > datetime.now()):
              num_upcoming_shows += 1;

      data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      })

  response={
        "count": len(venues),
        "data": data
    }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # TODO: replace with real venue data from the venues table, using venue_id - Done
    
    #write a query that pulls all venue information by ID
    data = db.session.query(Venue).get(venue_id)

    #TODO write a query that displays upcoming and past shows..



    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion - Done
    response = {}
    error = False
    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        address = request.form.get("address")
        phone = request.form.get("phone")
        image_link = request.form['image_link']
        website = request.form.get("website")
        facebook_link = request.form.get("facebook_link")
        genres = request.form.getlist("genres")
          # Created an if statement to accept True/False (wasn't working otherwise)
        seeking_talent = True if 'seeking_talent' in request.form else False 
        seeking_description = request.form['seeking_description']
        venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            image_link=image_link,
            website=website,
            genres=genres,
            facebook_link=facebook_link,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description
        )
        response["name"] = venue.name
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error == False:
              # on successful db insert, flash success
              flash('Venue ' + request.form['name'] + ' was successfully listed!')
        else:
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            flash("An error occurred. Venue " + request.form["name"] + " could not be listed.")
            print(sys.exc_info())
    return render_template('pages/home.html')


#  Update Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
   # TODO: populate form with values from venue with ID <venue_id> - Done
    form = VenueForm()
    # query database and filter by ID
    venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
 
    # populate the form with Data from DB
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.image_link.data = venue.image_link
    form.facebook_link.data = venue.facebook_link
    form.website.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    error = False

    # Get updated data from form
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    seeking_talent = True if 'seeking_talent' in request.form else False
    seeking_description = request.form['seeking_description']

    try:
        # get venue by ID
        venue = Venue.query.get(venue_id)

        # store updated data in variables
        venue.name = name
        venue.city = city
        venue.state = state
        venue.address = address
        venue.phone = phone
        venue.genres = genres
        venue.image_link = image_link
        venue.facebook_link = facebook_link
        venue.website = website
        venue.seeking_talent = seeking_talent
        venue.seeking_description = seeking_description

        # commit changes to the DB
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

        # Show banner
        if error:
            flash('An error occurred. Venue '+ name + ' could not be updated.','danger'
            )
        else:
            flash('Venue '+ name + ' was successfully updated!', 'success'
            )
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Delete Venue
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        # get venue, delete it, commit to db
        venue = Venue.query.filter(Venue.id == venue_id).first()
        name = venue.name

        db.session.delete(venue)
        db.session.commit()

       
    except:
        # if error, rollback session and flash error
        db.session.rollback()

        flash('An error occurred. Venue ' + name + ' wasn\'t deleted.')
    finally:
        db.session.close()
        if error:
          flash('There was an error')
        else:
          # flash if successful
          flash('Venue was successfully deleted.'
          )
    # return success
    return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage - DONE!


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database - Done

  # write a query to get all artists - done
  data = db.session.query(Artist).all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. - Done
  #write a search query using ilike() operator. 
    search_term = request.form.get('search_term', '')
    artists = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()
    data = []

    for artist in artists:
        num_upcoming_shows = 0
        shows = db.session.query(Show).filter(Show.artist_id == artist.id)
        for show in shows:
            if(show.start_time > datetime.now()):
                num_upcoming_shows += 1;
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming_shows
        })
    response={
        "count": len(artists),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # TODO: replace with real artist data - done
  # TODO write a query that produces upcoming shows, past shows
    # Create an artist page: 1)query all data from Artist by unique id
    artist = db.session.query(Artist).filter(Artist.id == artist_id).one()

    list_shows = db.session.query(Show).filter(Show.artist_id == artist_id)
    past_shows = []
    upcoming_shows = []

    for show in list_shows:
        venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id == show.venue_id).one()

        show_add = {
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime('%m/%d/%Y')
            }

        if (show.start_time < datetime.now()):
            #print(past_shows, file=sys.stderr)
            past_shows.append(show_add)
        else:
            print(show_add, file=sys.stderr)
            upcoming_shows.append(show_add)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  

  
  return redirect(url_for('show_artist', artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artists record in the db, instead
  # TODO: modify data to be the data object returned from db insertion - Done
    response = {}
    error = False
    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        phone = request.form.get("phone")
        image_link = request.form.get('image_link')
        website = request.form.get('website')
        facebook_link = request.form.get("facebook_link")
        genres = request.form.getlist("genres")
          # Created an if statement to accept True/False (wasn't working otherwise)
        seeking_venue = True if 'seeking_venue' in request.form else False 
        seeking_description = request.form['seeking_description']
        artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            image_link=image_link,
            genres=genres,
            website=website,
            facebook_link=facebook_link,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description
        )
        response["name"] = artist.name
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error == False:
              # on successful db insert, flash success
              flash('Artist ' + request.form['name'] + ' was successfully listed!')
        else:
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            flash("An error occurred. Artist " + request.form["name"] + " could not be listed.")
            print(sys.exc_info())
  
          # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  # displays list of shows at /shows - done
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
    #Query shows database and do a join with Venue and Artist
    
    get_shows = db.session.query(Show).join(Venue).join(Artist).all()
    data = []
    # probably use a for loop to display all information from shows.html.
    for show in get_shows:
      data.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name, 
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead - done
    error = False
    try: 
      artist_id = request.form['artist_id']
      venue_id = request.form['venue_id']
      start_time = request.form['start_time']

      print(request.form)

      show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
      db.session.add(show)
      db.session.commit()
    except: 
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally: 
      db.session.close()
    if error: 
      flash('An error occurred. Show could not be listed.')
    if not error: 
      flash('Show was successfully listed')
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
