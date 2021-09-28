import models
import random
import csv

# This class contains methods to create and manage Quiz.
class Quiz:
    def __init__(self, quiz_id=None, num_of_questions=None, marks=None):
        self.id = quiz_id
        self.num_of_questions = num_of_questions
        self.marks = marks

    def formulate(self):
        """Fetches the questions from database and creates a quiz made up of specified number of questions """
        all_questions = models.get_all_questions()

        # Filter the questions dictionary for the requested marks
        filtered_dict = {k: v for (
            k, v) in all_questions['questions'].items() if self.marks == v['marks']}

        # If the number of questions in DB are less than requested number of questions, retrive whatever is in DB
        num_questions = len(filtered_dict) if len(
            filtered_dict) < self.num_of_questions else self.num_of_questions

        # Pick random questions as per the requested number of questions.
        random_entry = random.choices(list(filtered_dict.items()), k = num_questions)

        quiz_paper = ' '.join(tuple(str(i[0]) for i in random_entry))
        answer_keys = ' '.join(
            tuple(str(i[1].get('key', None)) for i in random_entry))

        # insert a new record in quiz table
        response = models.insert_quiz(
            self.id, quiz_paper, answer_keys, num_questions, self.marks)
        return response

    def sort_questions_by_marks(self):
        all_questions = models.get_all_questions()
        sorted_dict = {k: v for k, v in sorted(
            all_questions['questions'].items(), key=lambda item: item[1].get('marks'))}
        for item in sorted_dict.items():
            print(item)

    def import_data(self, filename):
        with open(filename, 'r') as fin:
            dr = csv.DictReader(fin)
            to_db = [models.insert_question(i['question'], i['choice1'], i['choice2'],
                                            i['choice3'], i['choice4'], i['key'], i['marks'], i['remarks']) for i in dr]

    def render(self, quiz_id, user_id, answerkeys):
        """Evaluate the entered answer keys, calculate the score and create a record in the test_instance table"""
        result = []
        score = 0
        # Get the actual answer keys from quiz table
        quiz_details = models.get_quiz(quiz_id)

        # compare actual keys with the test answer keys
        actual_answer_keys = quiz_details['quiz'][2].split()

        if len(actual_answer_keys) < len(answerkeys):
            return {"message": "answerkeys size more than number of questions asked in quiz "}

        # Calculate the score and the result.
        for i in range(len(actual_answer_keys)):
            if i < len(answerkeys):
                if answerkeys[i] == int(actual_answer_keys[i]):
                    score = score + self.marks
                    result.append(self.marks)
                else:
                    result.append(0)
            else:
                result.append(0)

        answer_keys = ' '.join(tuple(str(i) for i in answerkeys))
        # insert a new record in the test_instance table
        response = models.insert_test_instance(
            quiz_id, user_id, answer_keys, score, result)

        return response

# # one time use. Uncomment and run below lines and comment after use.
# ob = Quiz(30001, 2, 2)
# # Create Quiz based on given number of questions and marks
# ob.formulate()

# # Load Questions from csv file into Database
# ob.import_data('quiz_data.csv')


# ob1 = Quiz(30002, 6, 2)
# ob1.formulate()
# ob2 = Quiz(30003, 5, 2)
# ob2.formulate()
# ob3 = Quiz(30004, 2, 1)
# ob3.formulate()
# ob7 = Quiz(30006, 10, 1)
# ob7.formulate()
# ob7 = Quiz(30007, 10, 2)
# ob7.formulate()

# ob6 = Quiz(30006, 7, 2)
# ob6.sort_questions_by_marks()
