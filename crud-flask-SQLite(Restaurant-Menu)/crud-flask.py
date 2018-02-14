#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, url_for, render_template, redirect, request, \
    flash, jsonify
from sqlalchemy import create_engine, and_
import os
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()
app = Flask('__name__')


# API endpoint for restaurants
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])



# API endpoint for restaurant menus
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, menu_id):
    menuItem = session.query(MenuItem).filter_by(
        id=menu_id).one()
    return jsonify(MenuItem=menuItem.serialize)


@app.route('/')
@app.route('/restaurants')
def restaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)


@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    if request.method == 'POST' and request.form['restaurant_name']:
        editRestaurant = session.query(
            Restaurant).filter_by(id=restaurant_id).one()
        editRestaurant.name = request.form['restaurant_name']
        session.add(editRestaurant)
        session.commit()
        flash("Restaurant edited")
        return redirect(url_for('restaurants'))
    else:
        restaurant = session.query(
            Restaurant).filter_by(id=restaurant_id).one()
        return render_template('restaurant_edit.html', restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    try:
        if request.method == 'POST':
            session.query(Restaurant).filter_by(id=restaurant_id).delete()
            # delete all menu associated with the restaurant as well.
            session.query(MenuItem).filter_by(
                restaurant_id=restaurant_id).delete()
            session.commit()
            flash('Restaurant deleted')
            return redirect(url_for('restaurants'))
        else:
            restaurant = session.query(
                Restaurant).filter_by(id=restaurant_id).one()
            return render_template(
                'restaurant_delete.html',
                restaurant=restaurant)
    except Exception as e:
        print "Could not delete restaurant"
        print e


@app.route('/restaurant/<int:restaurant_id>/menu')
def show_menu(restaurant_id):
    restaurant = \
        session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_items = \
        session.query(MenuItem).filter_by(restaurant_id=restaurant.id).all()
    return render_template('menu.html', restaurant=restaurant,
                           menu_items=menu_items)


@app.route('/menu/<int:restaurant_id>/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newMenuItem = MenuItem(restaurant_id=restaurant_id,
                               name=request.form['menu_name'],
                               price=request.form['menu_price'],
                               description=request.form['menu_description'
                                                        ])
        session.add(newMenuItem)
        session.commit()
        flash("You've added a new menu!")
        return redirect(url_for('show_menu',
                                restaurant_id=restaurant_id))
    else:

        restaurant = \
            session.query(Restaurant).filter_by(id=restaurant_id).one()
        return render_template('menu_new.html', restaurant=restaurant)


@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
    if request.method == 'POST' and request.form:
        try:
            newRestaurant = Restaurant(name=request.form['restaurant_name'])
            session.add(newRestaurant)
            session.commit()
            flash('New Restaurant added')
            return redirect(url_for('restaurants'))
        except Exception as e:
            print "Restaurant could not be added"
            print e
    else:
        return render_template('restaurant_new.html')


@app.route('/menu/<int:restaurant_id>/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    if request.method == 'POST' and request.form['menu_name']:
        editMenuItem = \
            session.query(MenuItem).filter_by(id=menu_id).one()
        editMenuItem.name = request.form['menu_name']
        editMenuItem.price = request.form['menu_price']
        editMenuItem.description = request.form['menu_description']
        session.add(editMenuItem)
        session.commit()
        flash('Menu edited')
        return redirect(url_for('show_menu',
                                restaurant_id=restaurant_id))
    else:
        restaurant = \
            session.query(Restaurant).filter_by(id=restaurant_id).one()
        menu_item = session.query(MenuItem).filter_by(id=menu_id).one()
        return render_template('menu_edit.html', restaurant=restaurant,
                               menu_item=menu_item)


@app.route('/menu/<int:restaurant_id>/<int:menu_id>/delete',
           methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    if request.method == 'POST':
        deleteMenuItem = \
            session.query(MenuItem).filter_by(id=menu_id).one()
        if deleteMenuItem:
            session.delete(deleteMenuItem)
            session.commit()
            flash('Menu deleted')
            return redirect(url_for('show_menu',
                                    restaurant_id=restaurant_id))
    else:
        restaurant = \
            session.query(Restaurant).filter_by(id=restaurant_id).one()
        menu_item = session.query(MenuItem).filter_by(id=menu_id).one()
        return render_template('menu_delete.html',
                               restaurant=restaurant,
                               menu_item=menu_item)


# Flask static file refresh
# https://gist.github.com/itsnauman/b3d386e4cecf97d59c94

@app.context_processor
def override_url_for():
    """
    Generate a new token on every request to prevent the browser from
    caching static files.
    """

    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


if __name__ == '__main__':
    app.secret_key = ':%$9898lkiuygjPOIYTYHK595*-*/)_('
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
