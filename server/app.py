#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    # def post(self):
    #     json = request.get_json()

    #     if User.query.filter_by(username = json['username']).first():
    #         return {'error': 'Username already exists, please try another username'}, 422
        
    #     user = User(
    #         username = json['username'],
    #         image_url = json['image_url'],
    #         bio = json['bio'],
    #     )
    #     user.password_hash = json['password']
            
    #     db.session.add(user)
    #     db.session.commit()

    #     session['user_id'] = user.id

    #     return user.to_dict(), 201
        
    def post(self):
        json = request.get_json()
        
        username = json.get('username')
        password = json.get('password')
        image_url = json.get('image_url', '') 
        bio = json.get('bio', '')  

        errors = {}

        if not username:
            errors['username'] = 'Username is required.'
        elif User.query.filter_by(username=username).first():
            errors['username'] = 'Username already exists.'
        
        if not password:
            errors['password'] = 'Password is required.'
        
        if errors:
            return {'errors': errors}, 422

        user = User(
            username=username,
            image_url=image_url,
            bio=bio
        )
        
        user.password_hash = password

        try:
            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id

            return user.to_dict(), 201

        except IntegrityError:
            db.session.rollback()
            return {'error': 'An error occurred while creating the user. Please try again.'}, 500

class CheckSession(Resource):
    # def get(self):
    #     user = User.query.filter(User.id == session.get('user_id')).first()
    #     if user:
    #         return user.to_dict(), 200
        
    #     return {'error': 'please login or signup'}, 401

    def get(self):
        # Check if 'user_id' is in the session
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                # Return user details as JSON
                return {
                    'id': user.id,
                    'username': user.username,
                    'image_url': user.image_url,
                    'bio': user.bio
                }, 200
        # If no user is logged in, return unauthorized error
        return {'error': 'Unauthorized'}, 401

class Login(Resource):
    pass

class Logout(Resource):
    pass

class RecipeIndex(Resource):
    pass

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)