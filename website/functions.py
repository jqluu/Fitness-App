# plot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd

# date 
from datetime import datetime, timedelta

# models
from .models import Weight, Workout, Exercise, workout_exercise, User

# weight avg
from collections import defaultdict
from statistics import mean


# Function to update the weight plot
def update_weight_plot(weight_data):
    df = pd.DataFrame(weight_data, columns=['Date', 'Weight'])

    # Convert Date column to datetime if it's not already in datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    plt.gcf().set_facecolor('grey')


    plt.plot(df['Date'], df['Weight'], marker='o', linestyle='-', color='blue')
    plt.xlabel('Date')
    plt.ylabel('Weight')
    plt.title('Weight Data Over Time')
    plt.grid(True)

    # Format x-axis ticks to show month and day only (exclude year)
    plt.gcf().autofmt_xdate()  # Rotates the dates for better readability
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))

    # Extract unique years from the data
    unique_years = df['Date'].dt.year.unique()

    # Display each unique year as a label on the plot
    for year in unique_years:
        year_data = df[df['Date'].dt.year == year]
        plt.text(
            year_data['Date'].iloc[0],  # x-coordinate for the label
            year_data['Weight'].max(),  # y-coordinate for the label (adjust as needed)
            f"Year: {year}",  # Text to display (Year: XXXX)
            ha='left', va='center',  # Alignment of the text
            fontsize=10,  # Adjust font size as needed
            color='gray'  # Text color
        )

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    img_data_uri = f"data:image/png;base64, {base64.b64encode(img.read()).decode()}"
    return img_data_uri


# calc weekly workout count
def weeklyWorkoutCount(user):

    # Get today's date
    today = datetime.now().date()
    # Calculate the start and end dates for the current week 
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6) 

    # Query workouts for the user within the current week
    workouts_this_week = Workout.query.filter(
        Workout.user_id == user.id,
        Workout.date >= start_of_week,
        Workout.date <= end_of_week
    ).all()

    return len(workouts_this_week)


# calc weekly weight avg gain/loss
def weightChange(user):

    # Get the user's weights for the last two weeks (assuming 'user_id' is the user's ID)
    today = datetime.now().date()
    two_weeks_ago = today - timedelta(days=14)

    # group last two weeks
    user_weights_last_two_weeks = Weight.query.filter_by(user_id=user.id).filter(
        Weight.date >= two_weeks_ago, Weight.date <= today
    ).order_by(Weight.date).all()

    # change in weight 
    if user_weights_last_two_weeks:
        earliest_weight = user_weights_last_two_weeks[0].data  # Assuming data is numeric
        latest_weight = user_weights_last_two_weeks[-1].data

        weight_change = float(latest_weight) - float(earliest_weight)
        return weight_change
    else:
        return 0
