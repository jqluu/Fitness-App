from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Weight
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        weight = request.form.get('weight')

        # if not weight.isdigit():
        #     flash('Please enter a valid weight.', category='error')
        # else:
        new_weight = Weight(data=weight, user_id=current_user.id)
        db.session.add(new_weight)
        db.session.commit()

        flash('Weight added.', category='success')

    return render_template("home.html", user=current_user)


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