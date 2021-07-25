import os
from flask import Flask, json, request, abort, jsonify
from sqlalchemy.sql.expression import true
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_category_dict():
    categories = Category.query.all()
    categories_dictionary = {}

    for category in categories:
        categories_dictionary[category.id] = category.type
    return categories_dictionary


def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={'/': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,POST,PUT,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():

        categories = create_category_dict()
        if (len(categories) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories,
            'total_categories': len(categories)
        })

    @app.route('/questions')
    def get_questions():

        selection = Question.query.all()
        current_questions = paginate_questions(request, selection)

        if (len(current_questions) == 0):
            abort(404)

        categories = create_category_dict()

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': categories
        }), 200

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question_by_id(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()

        if not question:
            abort(422)
        question.delete()
        selection = Question.query.all()
        current_question = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'deleted': question_id,
            'current_questions': current_question,
            'total_questions': len(selection)

        })

    @app.route('/questions', methods=['POST'])
    def create_or_search_new_question():
        body = request.get_json()
        search_term = body.get('searchTerm', None)
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:

            if not search_term:

                question = Question(question=new_question, answer=new_answer,
                                    category=new_category, difficulty=new_difficulty)

                if len(new_answer) == 0 or len(new_question) == 0:
                    abort(400)
                question.insert()
                selection = Question.query.all()

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': paginate_questions(request, selection),
                    'total_questions': len(selection)}), 200
            else:
                search_result = Question.query.filter(
                    Question.question.ilike(f'%{search_term}%')).all()
                if not search_result:

                    abort(404)

                return jsonify({
                    'success': True,
                    'total_questions': len(search_result),
                    'questions': paginate_questions(request, search_result)
                }), 200

        except:
            if not search_result:
                abort(404)

            abort(422)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_question_based_on_category(category_id):

        category = Category.query.get(category_id)
        if not category:
            abort(404)

        questions = Question.query.filter(
            Question.category == str(category_id)).all()

        if(questions is None):

            abort(404)
        return jsonify({
            'success': True,
            'current_category': category_id,
            'questions': paginate_questions(request, questions),
            'total_questions': len(questions)
        }), 200

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():

        body = request.get_json()

        prev_question = body.get('previous_questions')

        quiz_category = body.get('quiz_category')
        quiz_category_list = ['0', '1', '2', '3', '4', '5']
        if quiz_category['id'] not in quiz_category_list:
            abort(404)

        if (int(quiz_category['id']) == 0):
            questions = Question.query.all()
        else:
            questions = Question.query.filter(
                Question.category == quiz_category['id']).all()

        formated_questions = [question.format() for question in questions]

        total_questions = len(questions)

        next_question = formated_questions[random.randrange(
            0, len(formated_questions), 1)]

        while len(prev_question) != total_questions:

            next_question = formated_questions[random.randrange(
                0, len(formated_questions), 1)]

            if next_question['id'] not in prev_question:

                prev_question.append(next_question)

                return jsonify({
                    'success': True,
                    'question': next_question}), 200

        return jsonify({
            'success': True
        }), 200

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found',

        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable',

        }), 422

    @app.errorhandler(400)
    def bad_request(error):

        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'message': 'method not allowed',
            'error': 405
        }), 405
    return app
