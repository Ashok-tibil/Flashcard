# Store this code in 'app.py' file
import json

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re


app = Flask(__name__)

app.jinja_env.globals.update(len=len)

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mysql@123'
app.config['MYSQL_DB'] = 'flashcard'

mysql = MySQL(app)

print(mysql)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return redirect('start')
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route('/start', methods=['GET', 'POST'])
def start():
    print(request.method)
    if request.method == 'GET':
        msg = ''
        return render_template('start.html', msg=msg)

    if request.method == 'POST':
        if request.form.get('Create_quiz') == 'Create a Quiz':
            # Redirect to page1 if button1 is clicked
            return redirect('/choose_subject')
        elif request.form.get('Choose_Existing_quiz') == 'Choose from Existing Quiz':
            # Redirect to page2 if button2 is clicked
            return redirect('/subject')
        return render_template('start.html')

@app.route('/')
def home():
    return redirect(url_for('start'))


@app.route('/subject', methods=['GET', 'POST'])
def subject():
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT Subjects.Subject_name, Topics.Topic_name, Quiz_names.Quiz_Id, Quiz_names.Quiz_name FROM Quiz_names "
                       "INNER JOIN Topics ON Quiz_names.Topic_id = Topics.Topic_Id INNER JOIN Subjects ON Topics.Subject_Id = Subjects.Subject_Id;")
        subjectlist = cursor.fetchall()
        print(subjectlist)

        output = {}
        for item in subjectlist:
            subject = item['Subject_name']
            topic = item['Topic_name']
            quiz_id = item['Quiz_Id']
            quiz_name = item['Quiz_name']
            if subject not in output:
                output[subject] = {}
            if topic not in output[subject]:
                output[subject][topic] = []
            output[subject][topic].append({'id': quiz_id, 'name': quiz_name})
        return render_template('subject.html', subjectObject=json.dumps(output))

    if request.method == 'POST':
        print("form.........")
        print(request.form["quiz"])
        return redirect(url_for('flashcard_screen', topicId=int(request.form["quiz"])))


@app.route('/flashcard_screen/<int:topicId>', methods=['GET', 'POST'])
def flashcard_screen(topicId):
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # print(request.form["Topic_Id"])
        cursor.execute("SELECT Quiz_name from Quiz_names where Quiz_Id=" + str(topicId))
        quizname = cursor.fetchone()
        print(quizname)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT Question, Answer from Questions_Answers where Quiz_Id=" + str(topicId))
        topiclist = cursor.fetchall()
        print(list(topiclist))
    return render_template('flashcard_screen.html', qas=list(topiclist), quizname=quizname)


@app.route('/choose_subject', methods=['GET', 'POST'])
def choose_subject():
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * from Subjects")
        choose_subjectlist = cursor.fetchall()
        print(list(choose_subjectlist))
        return render_template('choose_subject.html', choose_subjectlist=list(choose_subjectlist))

    if request.method == 'POST':
        print(request.form)
        print(request.form["Subject_Id"])
        return redirect(url_for('choose_topic', subject_id=int(request.form["Subject_Id"])))


@app.route('/choose_topic/<int:subject_id>', methods=['GET', 'POST'])
def choose_topic(subject_id):
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute("SELECT Topic_Id, Topic_name from Topics")
        cursor.execute("SELECT Topic_Id, Topic_name from Topics where Subject_Id="+str(subject_id))
        choose_topiclist = cursor.fetchall()
        print(list(choose_topiclist))

        return render_template('choose_topic.html', choose_topiclist=choose_topiclist)

    if request.method == 'POST':
        print(request.form)
        print(request.form["Topic_Id"])
        return redirect(url_for('upload_key_terms_definition', topicid=request.form["Topic_Id"]))


@app.route('/upload_key_terms_definition/<int:topicid>', methods=['GET', 'POST'])
def upload_key_terms_definition(topicid):
    if request.method == 'GET':
        return render_template('upload_key_terms_definition.html', topicid=topicid)

    if request.method == 'POST':
        Quiz_name = request.form['Quiz_name']
        Question = request.form.getlist('Question')
        Answer = request.form.getlist('Answer')
        print(topicid)
        print(Quiz_name)
        print(Question)
        print(Answer)


        # inserting Quiz_name to the Quiz_names table
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        insert_quiz_name = "INSERT INTO Quiz_names (Quiz_name, Topic_id) VALUES (%s, %s)"
        try:
            cursor.execute(insert_quiz_name, (Quiz_name, topicid))
            mysql.connection.commit()
            Quiz_Id = cursor.lastrowid
            print(Quiz_Id)

            # Insert the Question and Answer into the Question_Answer table
            for i in range(len(Question)):
                question = Question[i]
                answer = Answer[i]
                print(question, answer)
                insert_question = "INSERT INTO Questions_Answers (quiz_id, question, answer) VALUES (%s, %s, %s)"
                cursor.execute(insert_question, (Quiz_Id, question, answer))
                mysql.connection.commit()
            data = {"status": 200, "message": 'Quiz added successfully'}

            return jsonify(data)
        except Exception as e:
            return jsonify({"status": 400, "message": "The given quiz name is already exists for the selected topic, please provide another quiz name."}), 400




