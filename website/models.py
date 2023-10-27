from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150))
    password = db.Column(db.String(150))
    weights = db.relationship('Weight')

class Weight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10))
    date = db.Column(db.DateTime(timezone=True), default=func.date())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# workout/exercise
# Define the association table for the many-to-many relationship
workout_exercise = db.Table(
    'workout_exercise',
    db.Column('workout_id', db.Integer, db.ForeignKey('workout.id')),
    db.Column('exercise_id', db.Integer, db.ForeignKey('exercise.id'))
)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    date = db.Column(db.DateTime(timezone=True), default=func.date())

    # exercise many to many relation
    exercises = db.relationship(
        'Exercise',
        secondary=workout_exercise,
        backref=db.backref('workouts', lazy='dynamic'),
        lazy='dynamic'
    )


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    
    # set class?
    # weight x reps x sets

