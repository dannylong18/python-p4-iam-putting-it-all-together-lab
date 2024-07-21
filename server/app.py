#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
        
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

            return {
                    'id': user.id,
                    'username': user.username,
                    'image_url': user.image_url,
                    'bio': user.bio
                }, 201

        except IntegrityError:
            db.session.rollback()
            return {'error': 'An error occurred while creating the user. Please try again.'}, 500

class CheckSession(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            return {
                    'id': user.id,
                    'username': user.username,
                    'image_url': user.image_url,
                    'bio': user.bio
                }, 200
        
        return {'error': 'please login or signup'}, 401

class Login(Resource):

    def post(self):
        json = request.get_json()
        username = json.get('username')
        password = json.get('password')

        user = User.query.filter(User.username == username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return {
                    'id': user.id,
                    'username': user.username,
                    'image_url': user.image_url,
                    'bio': user.bio
            }

        return {'error' : 'Incorrect name or password'}, 401

class Logout(Resource):
    def delete(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            session['user_id'] = None
            return {}, 204
        
        return {'error': 'user not logged in'}, 401

class RecipeIndex(Resource):

    def get(self):

        user = User.query.filter(User.id == session.get('user_id')).first()

        if not user:
            return {'error': 'Unauthorized'}, 401

        recipes = Recipe.query.filter_by(user_id=user.id).all()

        serialized_recipes = []
        for recipe in recipes:
            serialized_recipe = {
                'id': recipe.id,
                'title': recipe.title,
                'instructions': recipe.instructions,
                'minutes_to_complete': recipe.minutes_to_complete,
                'user': {
                    'username': user.username,
                    'image_url': user.image_url,
                    'bio': user.bio
                }
            }

            serialized_recipes.append(serialized_recipe)

        return serialized_recipes, 200
    
    def post(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        username = user.username
        bio = user.bio
        image_url = user.image_url

        if not user:
            return {'error', 'Unauthorized'}, 401
        
        json = request.get_json()

        title = json.get('title')
        instructions = json.get('instructions')
        minutes_to_complete = json.get('minutes_to_complete')
        user_id = user.id

        errors = {}
        
        if not title:
            errors['title'] = 'title is required.'

        if not instructions or len(instructions) < 50:
            errors['instructions'] = 'instructions are required and must be over 50 characters in length.'

        if not minutes_to_complete:
            errors['mintues_to_complete'] = 'minutes must be an integer'

        if errors:
            return {'errors': errors}, 422
    
        new_recipe = Recipe(
            title = title,
            instructions = instructions,
            minutes_to_complete = minutes_to_complete,
            user_id = user_id
        )

        try:
            db.session.add(new_recipe)
            db.session.commit()

            return {
                    'title': new_recipe.title,
                    'instructions': new_recipe.instructions,
                    'minutes_to_complete': new_recipe.minutes_to_complete,
                    'user': {
                        'username': username,
                        'bio': bio,
                        'image_url': image_url,
                    }
                }, 201

        except IntegrityError:
            db.session.rollback()
            return {'error': 'An error occurred while creating the user. Please try again.'}, 500




api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)