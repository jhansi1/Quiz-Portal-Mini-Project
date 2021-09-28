# one time setup
import sqlite3

# Queries to create tables
user_sql_query = "CREATE TABLE Users(id integer PRIMARY KEY, name varchar(255) not null, token varchar(10) unique);"

question_sql_query = "CREATE TABLE Questions(id integer PRIMARY KEY, question varchar(1000) unique not null, choice1 varchar(255) not null,choice2 varchar(255) not null,choice3 varchar(255) not null,choice4 varchar(255) not null, key integer not null, marks integer not null, remarks varchar(255));"

quiz_sql_query = "CREATE TABLE Quiz(id integer PRIMARY KEY, quizpaper varchar(2000) not null, answerkeys varchar(255) not null, num_of_questions integer, marks integer);"

test_instance_sql_query = "CREATE TABLE Test_instance(id integer PRIMARY KEY AUTOINCREMENT, quizid integer, userid integer, answerkeys varchar(255), score integer not null,FOREIGN KEY(quizid) REFERENCES Quiz(id),FOREIGN KEY(userid) REFERENCES Users(id));"


conn = sqlite3.connect("quiz.db")  # create or open the DB
conn.execute('PRAGMA foreign_keys = ON')  # enable foreign key constraint

cur = conn.cursor()
cur.execute(user_sql_query)
cur.execute(question_sql_query)
cur.execute(quiz_sql_query)
cur.execute(test_instance_sql_query)

cur.execute("INSERT INTO Users(id, name, token) VALUES(?,?,?)",
            (10000, "admin", "f186fe629b"))
cur.execute("INSERT INTO Questions(id, question, choice1, choice2, choice3, choice4, key, marks, remarks) VALUES(?,?,?,?,?,?,?,?,?)",
            (20000, "What is the national game of Bangladesh?", "Cricket", "Kabaddi", "Hockey", "Khokho", 2, 2, "Sports"))

conn.commit()  # journaling
conn.close()  # write to file
