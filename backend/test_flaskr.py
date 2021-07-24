
import os
import unittest
import json

from werkzeug import datastructures
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:Mo1234554321@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
   

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        self.new_question ={
            'question' : 'what is your name' , 
            'answer' : 'mohammed',
            'category' : '1' , 
            'difficulty' : 5
        }
            
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_paginated_questions(self):

        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
    

    def test_404_sent_requesting_beyond_valid_page(self):

        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')


    
    def test_delete_question(self):
        res = self.client().delete('/questions/7')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id==7).one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],7)
        self.assertTrue(data['total_questions'])
        self.assertEqual(question,None)




    def test_404_if_question_does_not_exist(self):

        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'unprocessable')



    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['created'])
        self.assertTrue(data['total_questions'])



        
    def test_405_if_book_creation_not_allowed(self):
        res = self.client().post('/questions/5', json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code,405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'method not allowed')
    

    def test_search_question(self):
        res = self.client().post('/questions',json={'searchTerm':'movie'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
    

    def test_404_search_not_found(self):
        res = self.client().post('/questions',json={'searchTerm':'Khalid'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')




    def test_get_question_based_on_category(self):



        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)


        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['current_category'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
    

    def test_404_get_questions_based_on_category(self):

        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    

    
        
        





    




         
    
    




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()