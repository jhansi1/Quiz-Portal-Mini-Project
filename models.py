# A class representing models.
import sqlite3 as sql
user_id = 10000
question_id = 20000


def insert_user(user_name, user_token):
    """ Adds new users to the database. """
    try:
        with sql.connect("quiz.db") as con:
            cur = con.cursor()
            global user_id
            res = cur.execute("SELECT max(id) FROM Users")
            max_id = res.fetchone()
            user_id = int(max_id[0]) + 1
            cur.execute(
                "INSERT INTO Users(id, name, token) VALUES(?,?,?)", (user_id, user_name, user_token))
            con.commit()
            status = 200
            msg = "User successfully added"
    except Exception as e:
        con.rollback()
        user_id = user_id - 1
        status = 400
        msg = e
    finally:
        con.close()
        return {"status": status, "message": str(msg), "new_user_id": user_id if status != 400 else None, "token": user_token if status != 400 else None}


def get_all_users():
    """ Returns all users details from the database. """
    con = sql.connect("quiz.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM Users")
    items = res.fetchall()
    item_dict = {}
    for item in items:
        item_dict[item[0]] = {'user_id': item[0], 'user_name': item[1],
                              'token': item[2]}
    con.close()
    return {"users": item_dict}


def get_user(user_id):
    """ Returns a user record from the database. """
    con = sql.connect("quiz.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM Users WHERE id = %d" % (user_id))
    item = res.fetchone()
    con.close()
    return {"user": item}


def get_user_by_token(user_token):
    """ Returns a user record for a given user token from the database. """
    con = sql.connect("quiz.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM Users WHERE token = '%s'" % (user_token))
    item = res.fetchone()
    con.close()
    return {"user": item[0] if item is not None else None}


def delete_user(user_id):
    """ Deletes a user record from the database. """
    user = get_user(user_id)
    if user['user'] is None:
        status = 400
        msg = 'User does not exist'
    else:
        con = sql.connect("quiz.db")
        cur = con.cursor()
        cur.execute("DELETE FROM Users WHERE id = %d" % (user_id))
        con.commit()
        status = 200
        msg = "User successfully deleted"
        con.close()
    return {"status": status, "message": str(msg)}


def insert_question(question, choice1, choice2, choice3, choice4, key, marks, remarks):
    """ Adds new questions to the database. """
    try:
        with sql.connect("quiz.db") as con:
            cur = con.cursor()
            global question_id
            res = cur.execute("SELECT max(id) FROM Questions")
            max_id = res.fetchone()
            question_id = int(max_id[0]) + 1
            cur.execute(
                "INSERT INTO Questions(id, question, choice1, choice2, choice3, choice4, key, marks, remarks) VALUES(?,?,?,?,?,?,?,?,?)", (question_id, question, choice1, choice2, choice3, choice4, key, marks, remarks))
            con.commit()
            status = 200
            msg = "Question successfully added"
    except Exception as e:
        con.rollback()
        question_id = question_id - 1
        status = 400
        msg = e
    finally:
        con.close()
        return {"status": status, "message": str(msg), "new_question_id": question_id if status != 400 else None}


def get_all_questions():
    """ Returns all questions from the database. """
    con = sql.connect("quiz.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM Questions")
    items = res.fetchall()
    item_dict = {}
    for item in items:
        item_dict[item[0]] = {"question": item[1], "choice1": item[2], "choice2": item[3],
                              "choice3": item[4], "choice4": item[5], "key": item[6], "marks": item[7], "remarks": item[8]}

    con.close()
    return {"questions": item_dict}


def get_question(ques_id):
    """ Returns a question for the given ID from the database. """
    con = sql.connect("quiz.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM Questions WHERE id = %d" % (ques_id))
    item = res.fetchone()
    con.close()
    return {"question": item}


def get_questions(ques_id):
    """ Returns questions for the given IDs from the database. """
    ids_input = ', '.join(ques_id.split(' '))
    con = sql.connect("quiz.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM Questions WHERE id in (%s)" % (ids_input))
    items = res.fetchall()
    item_dict = {}
    for item in items:
        item_dict[item[0]] = {"question": item[1], "choice1": item[2], "choice2": item[3],
                              "choice3": item[4], "choice4": item[5], "marks": item[7], "remarks": item[8]}

    con.close()
    return {"questions": item_dict}


def delete_question(ques_id):
    """ Deletes a question from the database. """
    question = get_question(ques_id)
    if question['question'] is None:
        status = 400
        msg = 'Requested question is not found in the Database'
    else:
        con = sql.connect("quiz.db")
        cur = con.cursor()
        cur.execute("DELETE FROM Questions WHERE id = %d" % (ques_id))
        con.commit()
        status = 200
        msg = "Question successfully deleted"
        con.close()
    return {"status": status, "message": str(msg)}


def insert_quiz(quiz_id, quiz_paper, answer_keys, num_of_questions, marks):
    """ Create a new quiz in the database. """
    try:
        with sql.connect("quiz.db") as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO Quiz(id, quizpaper, answerkeys, num_of_questions, marks) VALUES(?,?,?,?,?)", (quiz_id, quiz_paper, answer_keys, num_of_questions, marks))
            con.commit()
            status = 200
            msg = "Quiz successfully created"
    except Exception as e:
        con.rollback()
        status = 400
        msg = e
    finally:
        con.close()
        return {"status": status, "message": str(msg)}


def get_quiz(quiz_id):
    """ Returns a quiz for the given ID from the database. """
    con = sql.connect("quiz.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM Quiz WHERE id = %d" % (quiz_id))
    item = res.fetchone()
    con.close()
    return {"quiz": item}


def insert_test_instance(quiz_id, user_id, answerkeys, score, result):
    """ Adds new test instance to the database. """
    try:
        with sql.connect("quiz.db") as con:
            con.execute("PRAGMA foreign_keys = ON;")
            cur = con.cursor()
            cur.execute(
                "INSERT INTO Test_instance(quizid, userid, answerkeys, score) VALUES(?,?,?,?)", (int(quiz_id), int(user_id), answerkeys, int(score)))
            con.commit()
            status = 200
            msg = "Test instance successfully added"
    except Exception as e:
        con.rollback()
        status = 400
        msg = e
    finally:
        con.close()
        return {"status": status, "message": str(msg), "score": score if status != 400 else None, "result": result if status != 400 else None}


def get_test_instance(quiz_id, user_id):
    """ Returns a latest test instance for the given quizID and userID from the database. """
    con = sql.connect("quiz.db")
    cur = con.cursor()
    res = cur.execute(
        "SELECT * FROM Test_instance WHERE quizid = %d and userid = %d ORDER BY id DESC" % (quiz_id, user_id))
    item = res.fetchone()
    con.close()
    return {"testinstance": item}
