from app.models import User
from werkzeug.security import generate_password_hash
from flask_login import current_user
from test_auth import login, register_users, logout

def test_get_homepage(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to your finance tracker!" in response.data

def test_get_dashboard(client, db_setup):
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page." in response.data
    assert response.request.path == '/login'
    register_users(db_setup)
    login(client)
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/dashboard'

def test_get_profile(client, db_setup):
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page." in response.data
    assert response.request.path == '/login'
    register_users(db_setup)
    login(client)
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/profile'

def test_get_logging_info(client, db_setup):
    response = client.get('/logging-info', follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page." in response.data
    assert response.request.path == '/login'
    register_users(db_setup)
    login(client)
    response = client.get('/logging-info', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/logging-info'

def test_filter_dashboard(client, db_setup):
    response = client.post('/dashboard/filter', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page." in response.data
    assert response.request.path == '/login'
    register_users(db_setup)
    login(client)
    response = client.post('/dashboard/filter?kind=incomes', data={
        'timeframe': 'None',
        'start_date': '2026-01-01',
        'end_date': '2026-04-01'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"No pie chart data" in response.data
    assert response.request.path == '/dashboard'
    response = client.post('/dashboard/filter?kind=incomes', data={
        'timeframe': 'None',
        'start_date': '',
        'end_date': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"No pie chart data" not in response.data
    assert response.request.path == '/dashboard'
    response = client.post('/dashboard/filter?kind=expenses', data={
        'timeframe': 'None',
        'start_date': '2026-01-01',
        'end_date': '2026-04-01'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"No bar graph data" in response.data
    assert response.request.path == '/dashboard'
    response = client.post('/dashboard/filter?kind=expenses', data={
        'timeframe': 'None',
        'start_date': '',
        'end_date': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"No bar graph data" not in response.data
    assert response.request.path == '/dashboard'
    response = client.post('/dashboard/filter?kind=compares', data={
        'timeframe': 'None',
        'start_date': '2026-01-01',
        'end_date': '2026-04-01'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/dashboard'
    response = client.post('/dashboard/filter?kind=compares', data={
        'timeframe': 'None',
        'start_date': '',
        'end_date': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/dashboard'
