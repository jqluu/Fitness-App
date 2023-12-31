# flask 
from flask import Blueprint, render_template, request, flash, jsonify, Response, url_for, redirect
from flask_login import login_required, current_user
import json
import os

# models
from .models import Weight, Workout, Exercise, workout_exercise, FoodItem

# plot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd

from website.functions import update_weight_plot, weeklyWorkoutCount, weightChange, calcMaintCals, calcProtein, getCurrWeight, calcRemainingCals, calcRemainingProtein

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

# Get the current directory
current_directory = os.path.dirname(__file__)

# Define the path to the static/img directory
img_directory = os.path.join(current_directory, 'static', 'img')

# Save the uploaded file to the img directory
file_path = os.path.join(img_directory, 'user_avatar.jpg')

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
    count_goal = current_user.user_info.weeklyGoal



    # weight dependant
    if (Weight.query.filter_by(user_id=current_user.id).order_by(Weight.date.desc()).first()):
    # weight change
        weight_changes = weightChange(current_user)
        # maintenance calories
        maintCals = calcMaintCals(current_user)
        # rec protein intake
        recProtein = calcProtein(current_user)
        # remaining calories
        remainingCals = calcRemainingCals(current_user, maintCals)
        # remaining protein
        remainingProtein = calcRemainingProtein(current_user, recProtein)
    else:
        weight_changes = 0
        # default
        maintCals = 0
        recProtein = 0
        remainingCals = 0
        remainingProtein = 0

    # days active
    daysActive = Weight.query.filter_by(user_id=current_user.id).count()

    return render_template("home.html", user=current_user, graph_data=weight_plot_image, sorted_workouts=sorted_workouts, workout_count=workout_count, count_goal=count_goal, weight_changes=weight_changes, maintCals=maintCals, recProtein=recProtein, daysActive=daysActive, remainingProtein=remainingProtein, remainingCals=remainingCals)
    

# weight tracker
@views.route('/weighttracker', methods=['GET', 'POST'])
@login_required
def weighttracker():

    if (Weight.query.filter_by(user_id=current_user.id).order_by(Weight.date.desc()).first()):
        # maintenance calories
        maintCals = calcMaintCals(current_user)
        # rec protein intake
        recProtein = calcProtein(current_user)
        # remaining calories
        remainingCals = calcRemainingCals(current_user, maintCals)
        # remaining protein
        remainingProtein = calcRemainingProtein(current_user, recProtein)

    else:
        # default
        maintCals = 0
        recProtein = 0
        remainingCals = 0
        remainingProtein = 0
        
    # plot
    weight_data = generate_weight_plot_data()
    weight_plot_image = update_weight_plot(weight_data)

    # sorting dates to be displayed
    sortedByDate = current_user.weightLog.order_by(Weight.date.asc()).all()

    # adding a new date to db
    if request.method == 'POST':
        form_name = request.form.get('form_name')
        print("form name= " + form_name)
        print(request.form)
        if form_name == 'weightTrackerForm':
            weight = request.form.get('weight')
            selected_date = request.form.get('selected-date')

            if (selected_date):
                selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            else:
                selected_date = date.today()

            new_weight = Weight(data=weight, date=selected_date, user_id=current_user.id)
            db.session.add(new_weight)

        elif form_name == 'calorieLogForm':
            calorie_data = int(request.form['calories'])
            protein_data = int(request.form['protein'])
            carbs_data = int(request.form['carbs'])
            fats_data = int(request.form['fats'])
            selected_date = date.today()

            new_foodItem = FoodItem(calories=calorie_data, protein=protein_data, carbs=carbs_data, fats=fats_data, date=selected_date, user_id=current_user.id)
            
            db.session.add(new_foodItem)

        db.session.commit()
        flash('Data added.', category='success')

        weight_data = generate_weight_plot_data()
        weight_plot_image = update_weight_plot(weight_data)

    return render_template("weight_tracker.html", user=current_user, sortedByDate=sortedByDate, graph_data=weight_plot_image, maintCals=maintCals, recProtein=recProtein, remainingProtein=remainingProtein, remainingCals=remainingCals)


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
        # print(request.content_type)

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
            
            if (exercise_data['type'] == 'weightTraining'):
                weight = exercise_data['weight']
                exercise_type = exercise_data['type']
                new_exercise = Exercise(name=exercise_name, type=exercise_type, weight=weight, sets=sets, reps=reps)
            elif (exercise_data['type'] == 'cardio'):
                exercise_type = exercise_data['type']
                new_exercise = Exercise(name=exercise_name, type=exercise_type, sets=sets, reps=reps)

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

@views.route('/toggle-favorite', methods=['POST'])
def toggle_favorite():  
    workout = json.loads(request.data) 
    workoutId = workout['workoutId']
    workout = Workout.query.get(workoutId)

    if workout:
        if workout.user_id == current_user.id:
            print("favorited")
            workout.isFavorited = not workout.isFavorited
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

    # weight dependant
    if (Weight.query.filter_by(user_id=current_user.id).order_by(Weight.date.desc()).first()):
        # weight change
        weight_changes = weightChange(current_user)
        #
        current_weight = getCurrWeight(current_user)
        # maintenance calories
        maintCals = calcMaintCals(current_user)
        # rec protein intake
        recProtein = calcProtein(current_user)
    else:
        weight_changes = 0
        # maintenance calories
        maintCals = 0
        # rec protein intake
        recProtein = 0


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



    return render_template("analytics.html", user=current_user, graph_data=weight_plot_image, events=events, maintCals=maintCals, recProtein=recProtein, weight_changes=weight_changes, current_weight=current_weight)


# profile
@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    username = current_user.username
    feet = current_user.user_info.height // 12
    inches = current_user.user_info.height % 12
    sorted_workouts = sorted(current_user.workoutLog, key=attrgetter('date'))

    # edit profile
    if request.method == 'POST':
        # profile pic
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file.filename != '':
                print("File received:", file.filename)  # Check if file is received
                try:
                    file.save(file_path)
                    print("File saved successfully")  # Check if file is saved
                except Exception as e:
                    print("Error saving file:", e)

        # Access form data using request.form
        name = request.form['name']
        age = int(request.form['age'])
        bio = request.form['bio']
        gender = request.form['genderOptions']

        # convert string to data
        feet = int(request.form['feet'])
        inches = int(request.form['inches'])
        height = (feet * 12) + inches

        weight_goal = request.form['weightOptions']
        weekly_goal = int(request.form['weekly-goal'])

        # store it in the database
        current_user.user_info.name = name
        current_user.user_info.bio = bio
        current_user.user_info.age = age
        current_user.user_info.gender = gender
        current_user.user_info.height = height
        current_user.user_info.weightGoal = weight_goal
        current_user.user_info.weeklyGoal = weekly_goal


        db.session.commit()


    return render_template("profile.html", user=current_user, username=username, feet=feet, inches=inches, sorted_workouts=sorted_workouts)