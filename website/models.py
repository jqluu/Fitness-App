from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Date

class User(db.Model, UserMixin):
    # info
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150))
    password = db.Column(db.String(150))

    # data
    weightLog = db.relationship('Weight', backref='user', lazy='dynamic')
    workoutLog = db.relationship('Workout')
    user_info = db.relationship('UserInfo', backref='user', uselist=False)

class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    bio = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    height = db.Column(db.Integer)
    weightGoal = db.Column(db.String(10))
    weeklyGoal = db.Column(db.Integer)

    # Foreign key to link UserInfo with User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))



class Weight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10))
    date = db.Column(Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))



# workout/exercise
# many-to-many relationship
workout_exercise = db.Table(
    'workout_exercise',
    db.Column('workout_id', db.Integer, db.ForeignKey('workout.id')),
    db.Column('exercise_id', db.Integer, db.ForeignKey('exercise.id'))
)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    date = db.Column(Date)
    isFavorited = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    # exercise many to many relation
    exercises = db.relationship(
        'Exercise',
        secondary=workout_exercise,
        backref=db.backref('workouts', lazy='dynamic'),
        lazy='dynamic'
    )


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    type = db.Column(db.String(20))
    weight = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)



  

