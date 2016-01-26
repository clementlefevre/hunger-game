import datetime

from flask import render_template, redirect, url_for, abort, flash, request, \
    current_app
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from sqlalchemy.exc import IntegrityError

from . import main
from .forms import EditProfileForm, EditProfileAdminForm, AddRestaurantForm, DeleteRestaurantForm, Add_vote_comment
from .. import db
from ..models import Role, User, Restaurant, Vote
from ..decorators import admin_required


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)

    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))

    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/restaurants', methods=['GET', 'POST'])
def all_restaurants():
    restaurants = Restaurant.query.all()
    form = Add_vote_comment()

    user = User.query.filter_by(email=current_user.email).first()
    date = datetime.datetime.today()
    vote = Vote.query.filter_by(user=user).filter_by(date=datetime.date.today()).first()
    all_votes_today = Vote.query.filter_by(date=datetime.date.today()).all()

    sorted_restaurants = []

    for resto in restaurants:
        resto_vote = 0

        for today_vote in all_votes_today:
            if today_vote.restaurant_id == resto.id:
                resto_vote += 1
        sorted_restaurants.append((resto, resto_vote))
    sorted_restaurants.sort(key=lambda x: x[1], reverse=True)

    if vote == None:
        voted_restaurant_id = -1
    else:
        voted_restaurant_id = vote.restaurant.id

    if form.validate_on_submit():
        vote.comment = form.comment.data
        db.session.add(vote)
        db.session.commit()

    return render_template('restaurants.html', restaurants=zip(*sorted_restaurants)[0], user=user,
                           voted_restaurant_id=voted_restaurant_id, date=date, vote=vote, form=form)


@main.route('/restaurants/add', methods=['GET', 'POST'])
def add_restaurant():
    form = AddRestaurantForm()
    if form.validate_on_submit():
        name = form.name.data
        coordinates = form.coordinates.data
        phone = form.phone.data
        menu_url = form.menu_url.data
        new_restaurant = Restaurant(name=name, coordinates=coordinates, phone=phone, menu_url=menu_url)
        try:
            db.session.add(new_restaurant)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Could not save this restaurant', category='error')
        return redirect(url_for('.all_restaurants'))

    return render_template('_add_restaurant.html', form=form, title='add')


@main.route('/restaurants/edit/<int:id>', methods=['GET', 'POST'])
def edit_restaurant(id):
    form = AddRestaurantForm()
    restaurant = Restaurant.query.filter_by(id=id).first()

    if form.validate_on_submit():
        restaurant.name = form.name.data
        restaurant.coordinates = form.coordinates.data
        restaurant.phone = form.phone.data
        restaurant.menu_url = form.menu_url.data

        db.session.add(restaurant)
        db.session.commit()
        flash('Restaurant has been updated', category='info')
        return redirect(url_for('.all_restaurants'))

    form.name.data = restaurant.name
    form.coordinates.data = restaurant.coordinates
    form.phone.data = restaurant.phone
    form.menu_url.data = restaurant.menu_url
    return render_template('_add_restaurant.html', form=form, title='edit')


@main.route('/restaurants/delete/<int:id>', methods=['GET', 'POST'])
def delete_restaurant(id):
    form = DeleteRestaurantForm()
    restaurant = Restaurant.query.filter_by(id=id).first()

    if form.validate_on_submit():
        db.session.delete(restaurant)
        db.session.commit()
        flash("The restaurant has deleted")
        return redirect(url_for('.all_restaurants'))

    return render_template('_delete_restaurant.html', form=form, title='delete', name=restaurant.name)


@main.route('/restaurants/vote/<int:restaurant_id>', methods=['GET', 'POST'])
def vote_restaurant(restaurant_id):
    user = User.query.filter_by(email=current_user.email).first()
    has_voted = True
    current_vote = Vote.query.filter_by(user=user).filter_by(date=datetime.date.today()).first()
    if current_vote == None:
        has_voted = False

    if has_voted:
        db.session.delete(current_vote)
        db.session.commit()

    new_vote = Vote(user_id=user.id, restaurant_id=restaurant_id, date=datetime.date.today())
    try:
        db.session.add(new_vote)
        db.session.commit()
    except IntegrityError:
        flash('One man, One vote', category='warning')
        db.session.rollback()
    return redirect(url_for('.all_restaurants'))
