from flask import jsonify, abort, render_template, request

from . import app, db
from data.tasklist import tasks_list
from .models import User
from .models import Task
from .auth import basic_auth, token_auth

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users', methods=['POST'])
def create_user():
    # Check to make sure that the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    # Get the data from the request body
    data = request.json

    # Validate that the data has all of the required fields
    required_fields = ['firstName', 'lastName', 'username', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400

    # Pull the individual data from the body
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check to see if any current users already have that username and/or email
    check_users = db.session.execute(db.select(User).where( (User.username == username) | (User.email == email) )).scalars().all()
    if check_users:
        return {'error': "A user with that username and/or email already exists"}, 400

    # Create a new instance of user with the data from the request
    new_user = User(first_name=first_name, last_name=last_name,  username=username, email=email, password=password)

    return new_user.to_dict(), 201

@app.route('/token')
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    return user.get_token()
@app.route('/users/me')
@token_auth.login_required
def get_me():
    user = token_auth.current_user()
    return user.to_dict()

@app.route('/users', methods=['PUT'])
@token_auth.login_required
def update_user():
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    data = request.json
    allowed_fields = ['firstName', 'lastName', 'username', 'email', 'password']
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    update_data = {"first_name": first_name, "last_name": last_name, "username": username, "email": email, "password": password}
    current_user = token_auth.current_user()
    user = db.session.get(User, current_user.id)
    current_user.update(update_data)
    return current_user.to_dict()

@app.route('/users', methods=['DELETE'])
@token_auth.login_required
def delete_user():
    current_user = token_auth.current_user()
    user = db.session.get(User, current_user.id)
    if user:
        user.delete()
        return {'success': 'user deleted'}, 200
   

@app.route('/tasks')
def get_all_tasks():
    select_stmt = db.select(Task)
    search = request.args.get('search')
    if search:
        select_stmt = select_stmt.where(Task.title.ilike(f"%{search}%"))
    # Get the posts from the database
    tasks = db.session.execute(select_stmt).scalars().all()
    return [t.to_dict() for t in tasks]

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task_by_id(task_id):
    task = db.session.get(Task, task_id)
    if task:
        return task.to_dict()
    else:
        return {'error': f"Post with an ID of {task_id} does not exist"}, 404
@app.route('/tasks', methods=['POST'])
@token_auth.login_required
def create_task(): 
   
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
   
    data = request.json
   
    required_fields = ['title', 'description']
    missing_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    

    title = data.get('title')
    description = data.get('description')
    current_user = token_auth.current_user()
    
    new_task = Task(title=title, description=description, user_id=current_user.id)

    return new_task.to_dict(), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
@token_auth.login_required
def edit_task(task_id):
    if not request.is_json:
        return {'error': 'Your content type must be application/json'}, 400
    task = db.session.get(Task, task_id)
    if task is None:
        return {'error': f"task with ID #{task_id} does not exist"}, 404
    create_user = token_auth.current_user()
    if create_user is not task.author:
        return {'error': "this is not your task to edit"}, 403
    data = request.json
    task.update(**data)
    return task.to_dict()

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_auth.login_required
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        return {'error': f"No Task with id #{task_id}"}, 404
    create_user = token_auth.current_user()
    if task.author != create_user:
        return {'error': 'you dont have permision to delete this task'}, 403
    task.delete()
    return {'success': 'task deleted'}, 200
    
