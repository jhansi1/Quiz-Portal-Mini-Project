from flask import Flask, jsonify, request, render_template
from quiz_creator import Quiz
import models
import string
import secrets

app = Flask(__name__)
app.secret_key = 'super secret string'
app.config['JSON_SORT_KEYS'] = False

USER_TABLE_LIMIT = 10013
QUESTION_TABLE_LIMIT = 20013
ADMIN_TOKEN = 'f186fe629b'
ADMIN_ID = 10000


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/user/', methods=['POST', 'DELETE'])
def user():
    """ Only ADMIN is allowed to create and delete users.
       POST request: Creates new user in the database.
       DELETE request: Deletes a user record from the database.
    """
    if request.method == 'POST':
        data = request.get_json()
        user_name = data.get('name', None)
        token = data.get('token', None)
        users_details = models.get_all_users()

        global USER_TABLE_LIMIT, ADMIN_TOKEN
        if max(users_details['users']) >= USER_TABLE_LIMIT:
            return jsonify({"message": 'Database full, cannot create user', "status": 507})
        if token is None: 
            response = {
                "message": 'You must enter the admin token', "status": 403} 
        elif data and token == ADMIN_TOKEN:
            # Generate a 10 digit hex code
            hex_codes = "0123456789abcdef"
            user_token = ''.join(secrets.choice(hex_codes)
                                 for i in range(10))
            response = models.insert_user(user_name, user_token)
        else:
            response = {
                "message": 'You do not have access to the requested content - The token is not valid hexadecimal or not that of admin user', "status": 403}

    elif request.method == 'DELETE':
        data = request.get_json()
        user_id = data.get('user_id', None)
        token = data.get('token', None)

        if token is None or user_id is None: 
            response = {
                "message": 'You must pass both admin token and user ID', "status": 403} 
        elif data and user_id != ADMIN_ID and token == ADMIN_TOKEN:
            response = models.delete_user(user_id)
        else:
            response = {
                "message": "You are unauthorized to delete or have entered invalid hex token", "status": 403}

    return jsonify(response)


@app.route('/question/', methods=['POST', 'DELETE'])
def question():
    """Only ADMIN is allowed to create and delete questions.
       POST request: Creates new question in the database.
       DELETE request: Deletes a question from the database.
    """
    if request.method == 'POST':
        data = request.get_json()
        question = data.get('question', None)
        choice1 = data.get('choice1', None)
        choice2 = data.get('choice2', None)
        choice3 = data.get('choice3', None)
        choice4 = data.get('choice4', None)
        key = data.get('key', None)
        marks = data.get('marks', None)
        remarks = data.get('remarks', None)
        token = data.get('token', None)

        question_details = models.get_all_questions()

        global QUESTION_TABLE_LIMIT, ADMIN_TOKEN
        if max(question_details['questions']) >= QUESTION_TABLE_LIMIT:
            return jsonify({"message": 'Database full, cannot create questions', "status": 507})
        
        if token is None: 
            response = {
                "message": 'You must enter the admin token to add a question', "status": 403} 
        elif data and token == ADMIN_TOKEN:
            response = models.insert_question(
                question, choice1, choice2, choice3, choice4, key, marks, remarks)
        else:
            response = {
                "message": 'You do not have access to the requested content - The token is not valid hexadecimal or not that of admin user', "status": 403}

    elif request.method == 'DELETE':
        data = request.get_json()
        ques_id = data.get('ques_id', None)
        token = data.get('token', None)

        if token is None or ques_id is None: 
            response = {
                "message": 'You must enter the admin token and question ID to delete a question', "status": 403} 
        elif data and token == ADMIN_TOKEN:
            response = models.delete_question(ques_id)
        else:
            response = {
                "message": "You are unauthorized to delete question or have entered invalid hex token", "status": 403}

    return jsonify(response)


@app.route('/quiz/', methods=['GET', 'POST'])
def quiz():
    """GET request: Returns the quiz assigned to user.
       POST request: Tests the answers submitted for a quiz and returns total score, result list indicating individual score for each of the question answered.
    """
    if request.method == 'GET':
        data = request.get_json()
        user_token = data.get('token', None)
        quiz_id = data.get('quiz_id', None)

        user_details = models.get_user_by_token(user_token)
        user_id = user_details.get('user', None)

        if user_id and quiz_id:
            test_instance_details = models.get_test_instance(quiz_id, user_id)
            if test_instance_details.get('testinstance', None):
                quiz_details = models.get_quiz(quiz_id)

                if quiz_details.get('quiz', None):
                    response = models.get_questions(quiz_details['quiz'][1])
                else:
                    response = {
                        "message": "The quiz ID is invalid", "status": 403}
            else:
                response = {
                    "message": "You have entered incorrect quiz ID/ hex token", "status": 403}
        else:
            response = {
                "message": "You have entered invalid quiz ID/ hex token", "status": 403}

    elif request.method == 'POST':
        data = request.get_json()
        user_token = data.get('token', None)
        quiz_id = data.get('quiz_id', None)
        answerkeys = data.get('answerkeys', [])
        num_of_questions = data.get('num_of_questions', None)
        marks = data.get('marks', None)

        if user_token and quiz_id:
            user_details = models.get_user_by_token(user_token)
            user_id = user_details.get('user', None)
            quiz_details = models.get_quiz(quiz_id)

            if user_id is None:
                response = {
                    "message": "The user ID is invalid or token is not hexadecimal or not found in database", "status": 403}

            # Create a new quiz with the requested num of questions and marks if it doesn't exist.
            # Render the score and result array for the quiz test
            elif quiz_details.get('quiz') is None and num_of_questions and marks:
                ob = Quiz(quiz_id, num_of_questions, marks)
                ob.formulate()
                response = ob.render(quiz_id, user_id, answerkeys)

            # Render the score and result array for the quiz test
            elif user_id and quiz_id and num_of_questions and marks:
                ob = Quiz(quiz_id, num_of_questions, marks)
                response = ob.render(quiz_id, user_id, answerkeys)
            else:
                response = {
                    "message": "You must valid values to the following fields: user_token, quiz_id, num_of_questions, marks", "status": 403}
        else:
            response = {
                "message": "You must pass values to the following fields: user_token, quiz_id, num_of_questions, marks", "status": 403}

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
