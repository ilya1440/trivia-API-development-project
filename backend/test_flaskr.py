import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.user_name = 'postgres'
        self.password = '12345'
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(self.user_name, self.password, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.question = {
            'question': 'Who was the first president of the Russian Federation?',
            'answer': 'Boris Yeltsin',
            'category': 4,
            'difficulty': 2
        }

        self.question_invalid = {
            'question': 'Who was the first president of the Russian Federation?',
            'answer': 'Boris Yeltsin',
            'category': 'History',
            'difficulty': 2
        }

        self.search_term = {
            'searchTerm': 'which'
        }

        self.quizz_data = {
            'previous_questions': [1, 2, 7],
            'quiz_category': {
                'id': 0
            }
        }

        self.quizz_data_out = {
            'previous_questions': [x for x in range(0, 1000)],
            'quiz_category': {
                'id': 0
            }
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_questions(self):
        response = self.client().get('/questions?page=1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["categories"])
        self.assertTrue(data["total_questions"])

    def test_404_question_beyond_valid_page(self):
        response = self.client().get('/questions?page=450')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # Delete a different question in each attempt
    def test_delete_question(self):

        response = self.client().delete('/questions/6')
        data = json.loads(response.data)
        question = Question.query.filter(Question.id == 6).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 6)
        self.assertEqual(question, None)

        question.insert()

    def test_404_question_not_exist(self):
        response = self.client().delete('/questions/1000000')
        data = json.loads(response.data)

        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 404)
        self.assertEqual(data["message"], "resource not found")

    def test_create_new_question(self):
        response = self.client().post('/questions', json=self.question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])

    def test_invalid_new_question(self):
        response = self.client().post('/questions', json=self.question_invalid)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)

    def test_search_question(self):
        response = self.client().post('/questions/search', json=self.search_term)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    def test_get_questions_by_category(self):
        response = self.client().get('/categories/3/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["current_category"])
        self.assertTrue(data["total_questions"])

    def test_404_category_does_not_exist(self):
        response = self.client().get('/categories/1000000/questions')
        data = json.loads(response.data)

        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 404)
        self.assertEqual(data["message"], "resource not found")

    def test_play_quizz(self):
        response = self.client().post('/quizzes', json=self.quizz_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])
        self.assertNotIn(data["question"]["id"], self.quizz_data['previous_questions'])

    def test_play_quizz_out(self):
        response = self.client().post('/quizzes', json=self.quizz_data_out)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 501)
        self.assertEqual(data["success"], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()