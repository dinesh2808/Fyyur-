#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)


# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String()))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(500), default = '')
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(500), default = '')
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
  start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
  venue = db.relationship('Venue', backref= db.backref('Artist'))
  artist = db.relationship('Artist', backref= db.backref('Venue'))

# db.create_all()

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues_list = Venue.query.all() 
  data = []
  for venue in venues_list:
    print('in venue loop')
    print(venue)
    venue_info = {
      'city': venue.city,
      'state': venue.state,
      'venues': [{
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len(Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.utcnow()).all())
        }]
    }
    print(venue_info)
    if not data: # if data list is empty append
      print('data is empty')
      data.append(venue_info)
      print('data append')
      print(venue_info)
    else:
      available = False 
      temp = {}
      for d in data:
        if (venue.city == d['city']):
          available = True
          temp = d

      if available:
        temp['venues'].append(venue_info['venues'][0])
        vailable = False  
      else:
        print('here')
        data.append(venue_info)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venues = Venue.query.all()
  search_term = request.form['search_term']
  response = {
    "count": 0,
    "data": []
  }
  for venue in venues:
    if search_term.lower() in venue.name.lower():
      
      response["count"] += 1
      response["data"].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.utcnow()).all())
      })
    
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id


  venue = Venue.query.get(venue_id)
  print(venue)
  past_shows = Show.query.filter(Show.venue_id == venue_id, Show.start_time <= datetime.utcnow()).all()
  print(past_shows)
  upcoming_shows = Show.query.filter(Show.venue_id == venue_id, Show.start_time > datetime.utcnow()).all()
  print(upcoming_shows)
  
  def set_shows_list(list):
    temp = []
    for show in list:
      temp.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
      })
    return temp
    
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": set_shows_list(past_shows),
    "upcoming_shows": set_shows_list(upcoming_shows),
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    venue = Venue( 
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      address = request.form['address'],
      phone = request.form['phone'],
      genres = request.form.getlist('genres'),
      facebook_link = request.form['facebook_link'],
      website = request.form['website'],
      image_link = request.form['image_link'],
      seeking_talent = request.form.get('seeking_talent') != None,
      seeking_description = request.form['seeking_description']
    )
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except: 
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists_list = Artist.query.all()
  data = [] 
  for artist in artists_list:
    data.append({
      "id": artist.id ,
      "name": artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  artists = Artist.query.all()
  search_term = request.form['search_term']

  response = {
    "count": 0,
    "data": []
  }

  for artist in artists:
    if search_term.lower() in artist.name.lower():
      
      response["count"] += 1
      response["data"].append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": len(Show.query.filter(Show.artist_id == artist.id, Show.start_time > datetime.utcnow()).all())
      })


  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  artist = Artist.query.get(artist_id)
  past_shows = Show.query.filter(Show.artist_id == artist_id, Show.start_time <= datetime.utcnow()).all()
  upcoming_shows = Show.query.filter(Show.artist_id == artist_id, Show.start_time > datetime.utcnow()).all()
  
  
  def set_shows_list(list):
    temp = []
    for show in list:
      temp.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
      })
    return temp
    
  data={
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
    "past_shows": set_shows_list(past_shows),
    "upcoming_shows": set_shows_list(upcoming_shows),
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  artist={
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
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist = Artist.query.get(artist_id)
  error = False
  try:
    def edit_data(requested_data, old_data):
      if not request.form[requested_data]:
        return old_data
      else:
        if requested_data is 'genres':
          return request.form.getlist('genres')
        else:
          return request.form[requested_data]

    artist.name = edit_data('name', artist.name)
    artist.phone = edit_data('phone', artist.phone)
    artist.city = edit_data('city', artist.city)
    artist.state = edit_data('state', artist.state)
    artist.facebook_link = edit_data('facebook_link', artist.facebook_link)
    artist.website = edit_data('website', artist.website)
    artist.image_link = edit_data('image_link', artist.image_link)
    artist.seeking_venue = request.form.get('seeking_venue') != None
    artist.seeking_description = edit_data('seeking_description', artist.seeking_description)
    artist.genres = edit_data('genres', artist.genres)
    
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully Edited!')
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be Edited.')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  venue={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.get(venue_id)
  error = False
  try:
    def edit_data(requested_data, old_data):
      if not request.form[requested_data]:
        return old_data
      else:
        if requested_data is 'genres':
          return request.form.getlist('genres')
        else:
          return request.form[requested_data]

    venue.name = edit_data('name', venue.name)
    venue.phone = edit_data('phone', venue.phone)
    venue.city = edit_data('city', venue.city)
    venue.state = edit_data('state', venue.state)
    venue.facebook_link = edit_data('facebook_link', venue.facebook_link)
    venue.website = edit_data('website', venue.website)
    venue.image_link = edit_data('image_link', venue.image_link)
    venue.seeking_talent = request.form.get('seeking_talent') != None
    venue.seeking_description = edit_data('seeking_description', venue.seeking_description)
    venue.genres = edit_data('genres', venue.genres)

    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully Edited!')
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be Edited.')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  error = False
  try:
    # TODO: modify data to be the data object returned from db insertion
    artist = Artist(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      genres = request.form.getlist('genres'),
      facebook_link = request.form['facebook_link'],
      website = request.form['website'],
      image_link = request.form['image_link'],
      seeking_venue = request.form.get('seeking_venue') != None,
      seeking_description = request.form['seeking_description']
    )
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows_List = Show.query.all() 
  data = []
  for show in shows_List:
    data.append(
      {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
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
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    show = Show(artist_id = artist_id, venue_id = venue_id, start_time = start_time)
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  if error:
    flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
