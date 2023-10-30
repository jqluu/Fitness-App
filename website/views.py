from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Weight
from . import db
import json

# plot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

# db
import sqlite3

def generate_plot():
    data = [(1, 2), (2, 3), (3, 5), (4, 7)]
    x, y = zip(*data)

    fig, ax = plt.subplots()  # Create a figure and axis
    ax.plot(x, y)
    ax.set_xlabel('X-axis Label')
    ax.set_ylabel('Y-axis Label')
    ax.set_title('Sample Graph')

    # Save the plot to an image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    img_data_uri = f"data:image/png;base64, {base64.b64encode(img.read()).decode()}"

    return img_data_uri

views = Blueprint('views', __name__)

# home / dash
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    graph_data = generate_plot()

    print("graph_data:", graph_data)

    return render_template("home.html", user=current_user, graph_data=graph_data)
    


# weight tracker
@views.route('/weighttracker', methods=['GET', 'POST'])
@login_required
def weighttracker():
    if request.method == 'POST':
        weight = request.form.get('weight')
        new_weight = Weight(data=weight, user_id=current_user.id)
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
    
    return render_template("workout_log.html", user=current_user)


# analytics
@views.route('/analytics', methods=['GET', 'POST'])
@login_required
def analytics():
    # generate graph
    graph_data = generate_plot()

    print("graph_data:", graph_data)

    return render_template("analytics.html", user=current_user, graph_data=graph_data)


# data = Weight.query.all()
#     data_list = [(weight.date, weight.data) for weight in data]


# profile
@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():

    return render_template("profile.html", user=current_user)