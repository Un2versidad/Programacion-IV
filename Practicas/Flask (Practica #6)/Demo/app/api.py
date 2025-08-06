from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User

api = Blueprint('api', __name__)

@api.route('/token', methods=['POST'])
@jwt_required()
def get_token():
    identity = get_jwt_identity()
    return jsonify(token=identity), 200

@api.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    return jsonify(username=user.username, email=user.email), 200