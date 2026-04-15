from app.models import User
from werkzeug.security import generate_password_hash
from flask_login import current_user

# Helper for less repeated code  
def register_users(db_setup, number=1):
    users = [None] * number
    for i in range(number):
        user = User(email=f'email{i+1}@test.com', nickname=f'tester{i+1}', password=generate_password_hash('correct'), security_answers=['a','b','c'])
        users[i] = user
        db_setup.session.add(user)
    db_setup.session.commit()
    return users


def login(client, user_id=1):
    client.post('/login', data={
        'identity': f'email{user_id}@test.com',
        'password': 'correct'
    })

def logout(client):
    client.get('/logout', follow_redirects=True)

def test_register_success(client, db_setup):
    response = client.post('/register', data={
        'email': 'new@test.com',
        'nickname': 'newuser',
        'password': 'password123',
        'answer1': 'Hometown',
        'answer2': 'PetName',
        'answer3': 'MaidenName'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    assert db_setup.session.scalar(db_setup.select(User).filter_by(email='new@test.com')) is not None

def test_register_duplicate_email(client, db_setup):
    register_users(db_setup)
    response = client.post('/register', data={
        'email': 'email1@test.com',
        'nickname': 'different',
        'password': 'password123',
        'answer1': 'a', 'answer2': 'b', 'answer3': 'c'
    }, follow_redirects=True)
    user = db_setup.session.scalar(db_setup.select(User).filter_by(nickname='different'))
    assert user is None
    assert response.status_code == 200
    assert response.request.path == '/register'

def test_login_success_email(client, db_setup):
    register_users(db_setup)
    response = client.post('/login', data={
        'identity': 'email1@test.com',
        'password': 'correct'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome back" in response.data
    assert response.request.path == '/dashboard'
    with client.application.test_request_context():
        assert current_user.is_authenticated

def test_login_success_nickname(client, db_setup):
    register_users(db_setup)
    response = client.post('/login', data={
        'identity': 'tester1',
        'password': 'correct'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome back" in response.data
    assert response.request.path == '/dashboard'
    with client.application.test_request_context():
        assert current_user.is_authenticated

def test_login_invalid_password(client, db_setup):
    register_users(db_setup)
    response = client.post('/login', data={
        'identity': 'email1@test.com',
        'password': 'wrong'
    }, follow_redirects=True)
    assert b"Invalid credentials" in response.data
    assert response.request.path == '/login'
    with client.application.test_request_context():
        assert not current_user.is_authenticated

def test_login_invalid_email(client, db_setup):
    register_users(db_setup)
    response = client.post('/login', data={
        'identity': 'nonexistent@test.com',
        'password': 'correct'
    }, follow_redirects=True)
    assert b"Invalid credentials" in response.data
    assert response.request.path == '/login'
    with client.application.test_request_context():
        assert not current_user.is_authenticated      

def test_login_invalid_nickname(client, db_setup):
    register_users(db_setup)
    response = client.post('/login', data={
        'identity': 'not-tester',
        'password': 'correct'
    }, follow_redirects=True)
    assert b"Invalid credentials" in response.data
    assert response.request.path == '/login'
    with client.application.test_request_context():
        assert not current_user.is_authenticated

def test_login_security_success(client, db_setup):
    user = User(email='sec@test.com', nickname='sec_user', 
                password='hash', security_answers=['Hometown', 'Pet', 'Maiden'])
    db_setup.session.add(user)
    db_setup.session.commit()
    response = client.post('/login/security', data={
        'email': 'sec@test.com',
        'nickname': 'sec_user',
        'security_question': "What is your hometown?",
        'security_answer': 'hometown'
    }, follow_redirects=True)
    assert b"Welcome back" in response.data
    assert response.request.path == '/profile'

def test_login_security_fail(client, db_setup):
    user = User(email='sec@test.com', nickname='sec_user', 
                password='hash', security_answers=['Hometown', 'Pet', 'Maiden'])
    db_setup.session.add(user)
    db_setup.session.commit()
    response = client.post('/login/security', data={
        'email': 'sec@test.com',
        'nickname': 'sec_user',
        'security_question': "What is your hometown?",
        'security_answer': 'dallas'
    }, follow_redirects=True)
    assert b"Invalid credentials" in response.data
    assert response.request.path == '/login/security'

def test_logout(client, db_setup):
    register_users(db_setup, 2)
    client.post('/login', data={'identity': 'email1@test.com', 'password': 'correct'})   
    with client.application.test_request_context():
        assert current_user.is_authenticated 
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    with client.application.test_request_context():
        assert not current_user.is_authenticated
