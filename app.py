#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Artist, Venue, Show
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html',
                            new_venue_list = Venue.query.order_by(Venue.id.desc()).limit(10).all(),
                            new_artist_list = Artist.query.order_by(Artist.id.desc()).limit(10).all()
                          )


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    distinct_city_state = Venue.query.distinct(Venue.city, Venue.state).all()
    data = [dcs.filiter_venue_on_city_state for dcs in distinct_city_state]
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_terms = request.form.get('search_term', '')
    count = 0
    data = []
    for search_term in search_terms:
        venues = Venue.query.filter(Venue.name.ilike("%{}%".format(search_term)))
        response = {
            "count": venues.count(),
            "data": [venue.properties for venue in venues.all()]
        }
    return render_template('pages/search_venues.html', results=response, search_term=search_terms)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venues = Venue.query.filter(Venue.id == venue_id).one_or_none()
    if venues is None:
        abort(404)
    data = venues.properties_with_shows_details
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
    # TODO: modify data to be the data object returned from db insertion
    venue_form = VenueForm(request.form)
    error = False
    try:
        new_venue = Venue(
            name=venue_form.name.data,
            city=venue_form.city.data,
            state=venue_form.state.data,
            address=venue_form.address.data,
            phone=venue_form.phone.data,
            genres=','.join(venue_form.genres.data),
            facebook_link=venue_form.facebook_link.data
        )
        db.session.add(new_venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed')
        error = True
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        return redirect(url_for('index'))
    else:
        abort(500)

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route('/venues/<int:venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
      target = Venue.query.filter(Venue.id == venue_id)
      flash("Venue {} has been deleted successfully".format(target.one().name))
      target.delete()
      db.session.commit()
  except:
      error = True
      flash("An error occurred. Venue {} could not be deleted".format(target.one().name))
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if not error:
      return redirect(url_for('index'))
  else:
      abort(500)
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.all()
    data = [artist.properties for artist in artists]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term', '')
    filter_by_name_state_city = Artist.query().filter(
        search_term == Artist.name.ilike("%{}%".format(search_term))|
        search_term == Artist.state.ilike("%{}%".format(search_term))|
        search_term == Artist.city.ilike("%{}%".format(search_term)))
    response = {
        "count": artists.count(),
        "data": [artist.properties for artist in filter_by_name_state_city.all()]
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.filter(Artist.id == artist_id).one_or_none()

    if artist is None:
        abort(404)

    data = artist.properties_with_shows_details

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist_form = ArtistForm()

    target_artist = Artist.query.filter(Artist.id == artist_id).one_or_none()
    if target_artist is None:
        abort(500)

    target_artist_properties = target_artist.properties
    form_with_target_artist = ArtistForm(data=target_artist_properties)
    return render_template('forms/edit_artist.html', form=form_with_target_artist, artist=target_artist_properties)





@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    update_form = ArtistForm(request.form)
    error = False
    try:
        artist = Artist.query.filter(Artist.id==artist_id).one()
        artist.name = update_form.name.data,
        artist.genres = ','.join(update_form.genres.data),
        artist.city = update_form.city.data,
        artist.state = update_form.state.data,
        artist.phone = update_form.phone.data,
        artist.facebook_link = update_form.facebook_link.data,
        artist.image_link = update_form.image_link.data,
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except:
        error = True
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be updated.')
    finally:
        db.session.close()
    if not error:
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        abort(500)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue_form = VenueForm()

    target_venue = Venue.query.filter(Venue.id == venue_id).one_or_none()
    if target_venue is None:
        abort(500)

    target_venue_properties = target_venue.properties
    form_with_target_venue = VenueForm(data=target_venue_properties)
    return render_template('forms/edit_venue.html', form=form_with_target_venue, venue=target_venue_properties)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    update_form = VenueForm(request.form)
    error = False
    try:
        venue = Venue.query.filter(Venue.id == venue_id).one()
        venue.name = update_form.name.data,
        venue.address = update_form.address.data,
        venue.genres = ','.join(update_form.genres.data),
        venue.city = update_form.city.data,
        venue.state = update_form.state.data,
        venue.phone = update_form.phone.data,
        venue.facebook_link = update_form.facebook_link.data,
        venue.image_link = update_form.image_link.data,
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except:
        error = True
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be updated.')
    finally:
        db.session.close()
    if not error:
        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        abort(500)

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
    # TODO: modify data to be the data object returned from db insertion

    artist_form = ArtistForm(request.form)
    error = False
    try:
        new_artist = Artist(
            name=artist_form.name.data,
            city=artist_form.city.data,
            state=artist_form.state.data,
            phone=artist_form.phone.data,
            genres=','.join(artist_form.genres.data),
            facebook_link=artist_form.facebook_link.data
        )
        db.session.add(new_artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        error = True
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        return redirect(url_for('index'))
    else:
        abort(500)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows = Show.query.all()
    data = [show.properties_with_artist_venue for show in shows]
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
    show_form = ShowForm(request.form)
    error = False
    try:
        new_show = Show(
            artist_id=show_form.artist_id.data,
            venue_id=show_form.venue_id.data,
            start_time=show_form.start_time.data
        )
        db.session.add(new_show)
        db.session.commit()
    # on successful db insert, flash success
        flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    except:
        flash('An error occurred. Show could not be listed.')
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        return redirect(url_for('index'))
    else:
        abort(500)

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
