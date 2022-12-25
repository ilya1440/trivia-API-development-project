from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def format_categories():
    categories = Category.query.order_by(Category.id).all()
    categories = [category.format() for category in categories]
    categories = {category["id"]: category["type"] for category in categories}

    return categories


def paginate_questions(questions):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in questions]
    questions = questions[start:end]

    return questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    # specify origins that can access API
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # specify allowed methods and headers from response object
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = format_categories()

            return jsonify(
                {
                    "success": True,
                    "categories": categories
                }
            )
        except:
            abort(400)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            questions = Question.query.order_by(Question.id).all()
            paginated_questions = paginate_questions(questions)
            categories = format_categories()

            if len(paginated_questions) == 0:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "questions": paginated_questions,
                    "total_questions": len(questions),
                    "categories": categories,
                    "current_category": None
                }
            )
        except HTTPException as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            else:
                abort(400)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify(
                {
                    'success': True,
                    'deleted': question_id
                }
            )

        except HTTPException as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            else:
                abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        question = body.get('question', None),
        answer = body.get('answer', None),
        category = body.get('category', None),
        difficulty = body.get('difficulty', None)

        # prevent adding empty fields
        if ('',) in [question, answer, category, difficulty]:
            abort(422)

        try:
            question = Question(question=question,
                                answer=answer,
                                category=category,
                                difficulty=difficulty
                                )
            question.insert()

            return jsonify(
                {
                    'success': True,
                    'created': question.id
                }
            )

        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            search = request.get_json().get('searchTerm', None)
            search_results = \
                Question.query.order_by(Question.id).filter(Question.question.ilike("%{}%".format(search))).all()
            paginated_questions = paginate_questions(search_results)
            return jsonify(
                {
                    'success': True,
                    'questions': paginated_questions,
                    'total_questions': len(search_results),
                    'current_category': None
                }
            )
        except:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
    def get_questions_by_category(cat_id):
        try:
            questions = Question.query.filter(Question.category == cat_id).order_by(Question.id).all()
            questions = [question.format() for question in questions]
            current_category = Category.query.filter(Category.id == cat_id).one_or_none()
            if current_category is None:
                abort(404)
            current_category = current_category.format().get("type", None)

            return jsonify(
                {
                    "success": True,
                    "questions": questions,
                    "total_questions": len(questions),
                    "current_category": current_category
                }
            )

        except HTTPException as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            else:
                abort(400)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            request_data = request.get_json()
            previous_questions = request_data.get('previous_questions', None)
            current_category = request_data.get('quiz_category', None)
            current_category = current_category.get('id', 0)

            if current_category != 0:
                next_question = Question.query.filter(
                    Question.id.notin_(previous_questions), Question.category == current_category).order_by(
                    db.func.random()).first()
            else:
                next_question = Question.query.filter(
                    Question.id.notin_(previous_questions)).order_by(db.func.random()).first()

            if next_question:
                next_question = next_question.format()
                return jsonify(
                    {
                        'success': True,
                        'question': next_question
                    }
                )
            else:
                abort(501)

        except HTTPException as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            else:
                abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify(
            {
                "success": False,
                "error": 404,
                "message": "resource not found"
            }
        ), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(
            {
                "success": False,
                "error": 400,
                "message": "bad request"
            }
        ), 400

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                }
            ), 422,
        )

    @app.errorhandler(501)
    def not_implemented(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 501,
                    "message": "resource not supported"
                }
            ), 501,
        )

    return app
