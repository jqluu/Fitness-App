# flask 
from flask import Blueprint, render_template, request, flash, jsonify, Response
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

# db
from . import db
import sqlite3
from datetime import datetime  
from datetime import date

def generate_weight_plot():

    # Create a Pandas DataFrame from the retrieved data
    weights = Weight.query.all()
    data = [(weight.date, float(weight.data)) for weight in weights]
    df = pd.DataFrame(data, columns=['Date', 'Weight'])

    # Create graph
    plt.figure(figsize=(10, 6))
    plt.plot(df['Date'], df['Weight'])
    plt.xlabel('Date')
    plt.ylabel('Weight')
    plt.title('Weight Data Over Time')


    # Save the plot to an image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Return url
    img_data_uri = f"data:image/png;base64, {base64.b64encode(img.read()).decode()}"
    return img_data_uri


views = Blueprint('views', __name__)

# home / dash
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():

    graph_data = generate_weight_plot()
    # print("graph_data:", graph_data)

    return render_template("home.html", user=current_user, graph_data=graph_data)
    

# weight tracker
@views.route('/weighttracker', methods=['GET', 'POST'])
@login_required
def weighttracker():
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

    return render_template("weight_tracker.html", user=current_user)


@views.route('/delete-weight', methods=['POST'])
def delete_weight():  
    weight = json.loads(request.data) 
    weightId = weight['weightId']
    weight = Weight.query.get(weightId)
    if weight:
        if weight.user_id == current_user.id:
            db.session.delete(weight)
            db.session.commit()

    return jsonify({})


# workout log
@views.route('/workoutlog', methods=['GET', 'POST'])
@login_required
def workoutlog():
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

    return render_template("workout_log.html", user=current_user)


# analytics
@views.route('/analytics', methods=['GET', 'POST'])
@login_required
def analytics():
    # generate graphs
    graph_data = generate_weight_plot()
    #debug
    #print("graph_data:", graph_data)
    return render_template("analytics.html", user=current_user, graph_data=graph_data)


# profile
@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    username = current_user.username
    return render_template("profile.html", user=current_user, username=username)