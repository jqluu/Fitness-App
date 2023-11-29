# flask 
from flask import Blueprint, render_template, request, flash, jsonify, Response, url_for, redirect
from flask_login import login_required, current_user
import json

# models
from .models import Weight, Workout, Exercise, workout_exercise

# plot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd

from website.functions import update_weight_plot, weeklyWorkoutCount, weightChange

# db
from . import db
import sqlite3
from datetime import datetime  
from datetime import date
from sqlalchemy import desc
from operator import attrgetter

def generate_weight_plot_data():
    sortedByDate = current_user.weightLog.order_by(Weight.date.asc()).all()
    data = [(weight.date, float(weight.data)) for weight in sortedByDate]
    return data

views = Blueprint('views', __name__)

# home / dash
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():

    # recent workouts
    sorted_workouts = sorted(current_user.workoutLog, key=attrgetter('date'))

    # weight summary
    weight_data = generate_weight_plot_data()
    weight_plot_image = update_weight_plot(weight_data)
    # print("graph_data:", graph_data)

    # quickstats
    workout_count = weeklyWorkoutCount(current_user)
    count_goal = 4
    #weight change
    weight_changes = weightChange(current_user)

    return render_template("home.html", user=current_user, graph_data=weight_plot_image, sorted_workouts=sorted_workouts, workout_count=workout_count, count_goal=count_goal, weight_changes=weight_changes)
    

# weight tracker
@views.route('/weighttracker', methods=['GET', 'POST'])
@login_required
def weighttracker():

    # plot
    weight_data = generate_weight_plot_data()
    weight_plot_image = update_weight_plot(weight_data)

    # sorting dates to be displayed
    sortedByDate = current_user.weightLog.order_by(Weight.date.asc()).all()

    # adding a new date to db
    if request.method == 'POST':
        weight = request.form.get('weight')
        selected_date = request.form.get('selected-date')

        if (selected_date):
            selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
        else:
            selected_date = date.today()

        new_weight = Weight(data=weight, date=selected_date, user_id=current_user.id)
        db.session.add(new_weight)
        db.session.commit()
        flash('Weight added.', category='success')
        weight_data = generate_weight_plot_data()
        weight_plot_image = update_weight_plot(weight_data)

    return render_template("weight_tracker.html", user=current_user, sortedByDate=sortedByDate, graph_data=weight_plot_image)


# delete weight
@views.route('/delete-weight', methods=['POST'])
def delete_weight():  
    weight = json.loads(request.data) 
    weightId = weight['weightId']
    weight = Weight.query.get(weightId)

    if weight:
        if weight.user_id == current_user.id:
            db.session.delete(weight)
            db.session.commit()

            # After deletion, update the plot and send the updated plot data back
            weight_data = generate_weight_plot_data()
            updated_plot = update_weight_plot(weight_data)
            return redirect(url_for('views.weighttracker', graph_data=updated_plot))

    flash('You are not authorized to delete this weight.', category='error')
    return redirect(url_for('views.weighttracker'))


# workout log
@views.route('/workoutlog', methods=['GET', 'POST'])
@login_required
def workoutlog():

    sorted_workouts = sorted(current_user.workoutLog, key=attrgetter('date'))

    if request.method == 'POST':
        print(request.content_type)

        workout_data = request.json  # Get the JSON data sent from the frontend
        print(workout_data)

        # Extract workout details (title, date, exercises)
        title = workout_data.get('title')
        selected_date = workout_data.get('date')
        exercises = workout_data.get('exercises')
        workout_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

        # Create a new Workout instance
        new_workout = Workout(name=title, date=workout_date, user_id=current_user.id)

        # Create Exercise instances and associate with the workout
        for exercise_data in exercises:
            exercise_name = exercise_data['name']
            sets = exercise_data['sets']
            reps = exercise_data['reps']

            new_exercise = Exercise(name=exercise_name, sets=sets, reps=reps)
            new_workout.exercises.append(new_exercise)

        # Add the new workout to the database session and commit changes
        db.session.add(new_workout)
        db.session.commit()
        flash('Workout added.', category='success')


    return render_template("workout_log.html", user=current_user, sorted_workouts=sorted_workouts)

# delete workout
@views.route('/delete-workout', methods=['POST'])
def delete_workout():  
    workout = json.loads(request.data) 
    workoutId = workout['workoutId']
    workout = Workout.query.get(workoutId)
    if workout:
        if workout.user_id == current_user.id:
            db.session.delete(workout)
            db.session.commit()

    return jsonify({})


# analytics
@views.route('/analytics', methods=['GET', 'POST'])
@login_required
def analytics():
    # generate graphs
    weight_data = generate_weight_plot_data()
    weight_plot_image = update_weight_plot(weight_data)
    #debug
    #print("graph_data:", graph_data)

    # calendar events
    workouts = Workout.query.all()

    # Convert Workout instances to a list of dictionaries
    events = []
    for workout in workouts:
        event = {
            'title': workout.name,
            'start': workout.date.strftime('%Y-%m-%d')
        }
        events.append(event)



    return render_template("analytics.html", user=current_user, graph_data=weight_plot_image, events=events)


# profile
@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    username = current_user.username
    return render_template("profile.html", user=current_user, username=username)