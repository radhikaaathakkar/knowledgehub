from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import pymysql

app = Flask(__name__)

# MySQL database configuration
db_config = {
    'host': 'admin.csisz6betj9n.us-east-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'radhika12345',
    'database': 'logindb',
}

# Function to validate login credentials
def validate_login(username, password):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # Check if the username and password match any record in the logintable
            sql = "SELECT * FROM logintable WHERE username=%s AND password=%s"
            cursor.execute(sql, (username, password))
            result = cursor.fetchone()
            return result is not None
    finally:
        connection.close()

# Function to check if a username already exists in the logintable
def username_exists(username):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM logintable WHERE username=%s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            return result is not None
    finally:
        connection.close()

# Function to register a new user
def register_user(username, password, email, phonenumber, address):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # Check if the username already exists
            if username_exists(username):
                return False, "Username already exists"

            # Insert the new user into the logintable
            sql = "INSERT INTO logintable (username, password, email, phonenumber, address) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (username, password, email, phonenumber, address))
            connection.commit()

            return True, None
    finally:
        connection.close()

# Function to post a question
def post_question(username, question_text):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # Insert the new question into the 'forms' table
            sql = "INSERT INTO forms (username, question_text) VALUES (%s, %s)"
            cursor.execute(sql, (username, question_text))
            connection.commit()
    finally:
        connection.close()

# Function to retrieve questions from the 'forms' table
def get_questions():
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # Retrieve all questions from the 'forms' table
            sql = "SELECT * FROM forms"
            cursor.execute(sql)
            questions = cursor.fetchall()
            print("Questions:", questions)  # Add this line for debugging
            return questions
    finally:
        connection.close()


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form['username']
    password = request.form['password']

    if validate_login(username, password):
        # If login is successful, redirect to the appropriate page
        if username == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    else:
        # If login fails, display an error message
        return render_template('login.html', error="Invalid username or password")

@app.route('/user')
def user_dashboard():
    # Retrieve questions from the 'forms' table
    questions = get_questions()
    return render_template('user.html', questions=questions)

@app.route('/admin')
def admin_dashboard():
    # Only allow access to the admin page if the user is logged in
    return render_template('admin.html')

@app.route('/add_material', methods=['POST'])
def add_material():
    # Path to the JSON file
    json_file_path = 'static/study_materials.json'

    try:
        # Load existing data from the JSON file
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                data = json.load(file)
        else:
            # If the file doesn't exist, start with an empty list
            data = []
    except FileNotFoundError:
        # If there's an issue with the file, start with an empty list
        data = []

    # Get the new material details from the request
    new_material = {
        'course': request.form['course'],
        'subject': request.form['subject'],
        'semester': request.form['semester'],
        'material': request.form['material'],
        'image': request.form['image'],
        'description': request.form['description']
    }

    # Add the new material to the existing data
    data.append(new_material)

    # Write the updated data back to the JSON file
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=2)

    return jsonify({"status": "success"})

@app.route('/delete_material', methods=['POST'])
def delete_material():
    # Path to the JSON file
    json_file_path = 'static/study_materials.json'

    try:
        # Load existing data from the JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist, return an error response
        return jsonify({"status": "error", "message": "JSON file not found"})

    # Get the details for the material to be deleted from the request
    course = request.form['course']
    subject = request.form['subject']
    semester = request.form['semester']

    # Find and remove the matching record
    matching_records = [record for record in data if record['course'] == course
                                                 and record['subject'] == subject
                                                 and record['semester'] == semester]

    if matching_records:
        # Remove the first matching record (assuming there should be only one)
        data.remove(matching_records[0])

        # Write the updated data back to the JSON file
        with open(json_file_path, 'w') as file:
            json.dump(data, file, indent=2)

        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Record not found"})

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    phonenumber = request.form['phonenumber']
    address = request.form['address']

    success, error_message = register_user(username, password, email, phonenumber, address)

    if success:
        # Redirect to the login page after successful registration
        return redirect(url_for('login'))
    else:
        # If registration fails, display an error message
        return render_template('signup.html', error=error_message)

@app.route('/blog')
def blog():
    # Retrieve questions from the 'forms' table
    questions = get_questions()
    return render_template('blog.html', questions=questions)

# Flask route to handle posting a question
@app.route('/post_question', methods=['POST'])
def post_question_route():
    # Get the question details from the form
    username = request.form['username']
    question_text = request.form['question_text']

    # Post the question to the database
    post_question(username, question_text)

    # Redirect to the blog page after posting the question
    return redirect(url_for('blog'))

if __name__ == '__main__':
    app.run(debug=True)
