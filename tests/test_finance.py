from datetime import datetime
from app.models import User, Expense, Income, Category, Budget
from werkzeug.security import generate_password_hash
from test_auth import login, register_users, logout

def add_expense(db_setup, user, number=1):
    for i in range(number):
        day = f'0{i+1}'
        if i >= 9:
            day = f'{i+1}'
        expense = Expense(
            date=datetime.strptime(f'12-{day}-2025', '%m-%d-%Y').date(), 
            amount=50.00 + i, 
            where=f'Location{i+1}', 
            category='None', 
            description='',
            recurring=False, 
            user_id=user.id)
        db_setup.session.add(expense)
    db_setup.session.commit()

def add_income(db_setup, user, number=1):
    for i in range(number):
        day = f'0{i+1}'
        if i >= 9:
            day = f'{i+1}'
        income = Income(
            date=datetime.strptime(f'12-{day}-2025', '%m-%d-%Y').date(),
            amount=50.00 + i,
            source=f'Location{i+1}',
            category='None',
            description='',
            recurring=False,
            user_id=user.id
        )
        db_setup.session.add(income)
    db_setup.session.commit()

def add_category(db_setup, user, number=1, type='e'):
    cat_type = "Expense" if type == 'e' else "Income"
    for i in range(number):
        category = Category(
            name=f'Category{i+1}',
            description='',
            type=cat_type,
            user_id=user.id)
        db_setup.session.add(category)
    db_setup.session.commit()

def add_budget(db_setup, user, number=1):
    for i in range(number):
        budget = Budget(
            category=f'Budget{i+1}',
            amount=50 + i,
            user_id=user.id)
        db_setup.session.add(budget)
    db_setup.session.commit()

### Expense tests ###

def test_get_expenses_page(client, db_setup):
    register_users(db_setup)
    login(client)
    response = client.get('/expenses', follow_redirects=True)
    assert response.status_code == 200
    assert b"Your Expenses" in response.data
    assert response.request.path == '/expenses'
    logout(client)
    response = client.get('/expenses', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'

def test_get_add_expense_page(client, db_setup):
    register_users(db_setup)
    login(client)
    response = client.get('/expenses/add', follow_redirects=True)
    assert response.status_code == 200
    assert b"Add an expense" in response.data
    assert response.request.path == '/expenses/add'
    logout(client)
    response = client.get('/expenses/add', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'

def test_add_expense(client, db_setup):
    users = register_users(db_setup)
    login(client)
    response = client.post('/expenses/add', data={
        'date': '2025-12-01',
        'amount': 50.00,
        'where': 'Location',
        'category': 'None',
        'description': ''
    }, follow_redirects=True)
    expense = db_setup.session.scalar(db_setup.select(Expense).filter_by(user_id=users[0].id))
    assert expense is not None
    assert expense.amount == 50.00
    assert expense.category == 'None'
    assert expense.where == 'Location' 
    assert expense.id == 1
    assert b"Location" in response.data
    assert response.status_code == 200
    assert response.request.path == '/expenses'
    logout(client)
    response = client.post('/expenses/add', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'

def test_get_edit_expense_page(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_expense(db_setup, users[0])
    response = client.get('/expenses/edit?id=1', follow_redirects=True)
    assert response.status_code == 200
    assert b"Edit Expense" in response.data
    assert b"Location1" in response.data
    assert response.request.path == '/expenses/edit'
    response = client.get('/expenses/edit?id=2', follow_redirects=True)
    assert response.status_code == 404
    assert b"404" in response.data
    assert response.request.path == '/expenses/edit'
    logout(client)
    response = client.get('/expenses/edit?id=1', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.get('/expenses/edit?id=1', follow_redirects=True)
    assert response.status_code == 404
    assert b"404" in response.data
    assert response.request.path == '/expenses/edit'

def test_edit_expense(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_expense(db_setup, users[0])
    expense = db_setup.session.scalar(db_setup.select(Expense).filter_by(user_id=users[0].id, id=1))
    assert expense is not None
    old_id = expense.id
    assert expense.amount == 50.00
    assert expense.category == 'None'
    response = client.post('/expenses/edit?id=1', data={
        'date': '2025-12-01',
        'amount': 75.00,
        'where': 'new location',
        'category': 'Food',
        'description': 'edited'
    }, follow_redirects=True)
    expense = db_setup.session.scalar(db_setup.select(Expense).filter_by(user_id=users[0].id, id=1))
    assert expense is not None
    assert expense.user_id == users[0].id
    assert expense.id == old_id
    assert expense.amount == 75.00
    assert expense.category == 'Food'
    assert b"New location" in response.data
    assert b"Location1" not in response.data
    assert response.status_code == 200
    assert response.request.path == '/expenses'
    response = client.post('/expenses/edit?id=2', data={}, follow_redirects=True)
    assert b"404" in response.data
    assert response.status_code == 404
    assert response.request.path == '/expenses/edit'
    logout(client)
    response = client.post('/expenses/edit?id=1', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.post('/expenses/edit?id=1', data={}, follow_redirects=True)
    assert b"404" in response.data
    assert response.status_code == 404
    assert response.request.path == '/expenses/edit'

def test_get_delete_expense_page(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_expense(db_setup, users[0], 2)
    response = client.get('/expenses/delete?id=1', follow_redirects=True)
    assert response.status_code == 200
    assert b"Delete" in response.data
    assert b"Location1" in response.data
    assert response.request.path == '/expenses/delete'
    response = client.get('/expenses/delete?id=3', follow_redirects=True)
    assert response.status_code == 404
    assert b"404" in response.data
    assert response.request.path == '/expenses/delete'
    logout(client)
    response = client.get('/expenses/delete?id=2', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.get('/expenses/delete?id=2', follow_redirects=True)
    assert response.status_code == 404
    assert b"404" in response.data
    assert response.request.path == '/expenses/delete'

def test_delete_expense(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_expense(db_setup, users[0], 2)
    expense = db_setup.session.scalar(db_setup.select(Expense).filter_by(user_id=users[0].id, id=1))
    assert expense is not None
    response = client.post('/expenses/delete?id=1', data={'id': 1}, follow_redirects=True)
    expense = db_setup.session.scalar(db_setup.select(Expense).filter_by(user_id=users[0].id, id=1))
    assert expense is None
    assert b"Location1" not in response.data
    assert response.status_code == 200
    assert response.request.path == '/expenses'
    response = client.post('/expenses/delete?id=1', data={'id': 1}, follow_redirects=True)
    assert b"404" in response.data
    assert response.status_code == 404
    assert response.request.path == '/expenses/delete'
    logout(client)
    response = client.post('/expenses/delete?id=2', data={'id': 2}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.post('/expenses/delete?id=2', data={'id': 2}, follow_redirects=True)
    assert b"404" in response.data
    assert response.status_code == 404
    assert response.request.path == '/expenses/delete'

def test_filter_expenses(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_expense(db_setup, users[0], 6)
    response = client.post('/expenses/filter', data={
        'start_date': None,
        'end_date': '2026-03-01',
        'min_amount': 51.00,
        'max_amount': 53.00,
        'categories': None,
        'where': 'location1, location2, location3, location6'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/expenses'
    assert b"Location1" not in response.data
    assert b"Location2" in response.data
    assert b"Location3" in response.data
    assert b"Location6" not in response.data
    logout(client)
    response = client.post('/expenses/filter', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.post('/expenses/filter', data={
        'start_date': None,
        'end_date': '2026-03-01',
        'min_amount': 51.00,
        'max_amount': 53.00,
        'categories': None,
        'where': 'location1, location2, location3, location6'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/expenses'
    assert b"Location" not in response.data

### Income tests ###

def test_get_incomes_page(client, db_setup):
    register_users(db_setup)
    login(client)
    response = client.get('/incomes', follow_redirects=True)
    assert response.status_code == 200
    assert b"Your Incomes" in response.data
    assert response.request.path == '/incomes'
    logout(client)
    response = client.get('/incomes', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'

def test_get_add_income_page(client, db_setup):
    register_users(db_setup)
    login(client)
    response = client.get('/incomes/add', follow_redirects=True)
    assert response.status_code == 200
    assert b"Add an income" in response.data
    assert response.request.path == '/incomes/add'
    logout(client)
    response = client.get('/incomes', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'

def test_add_income(client, db_setup):
    users = register_users(db_setup)
    login(client)
    response = client.post('/incomes/add', data={
        'date': '2025-12-01',
        'amount': 50.00,
        'source': 'location',
        'category': 'None',
        'description': ''
    }, follow_redirects=True)
    income = db_setup.session.scalar(db_setup.select(Income).filter_by(user_id=users[0].id))
    assert income is not None
    assert income.amount == 50.00
    assert income.category == 'None'
    assert income.source == 'Location'
    assert b"Location" in response.data
    assert response.status_code == 200
    assert response.request.path == '/incomes'
    logout(client)
    response = client.post('/incomes/add', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'

def test_get_edit_income_page(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_income(db_setup, users[0])
    response = client.get('/incomes/edit?id=1', follow_redirects=True)
    assert response.status_code == 200
    assert b"Edit Income" in response.data
    assert b"Location1" in response.data
    assert response.request.path == '/incomes/edit'
    response = client.get('/incomes/edit?id=2', follow_redirects=True)
    assert response.status_code == 404
    assert b"404" in response.data
    assert response.request.path == '/incomes/edit'
    logout(client)
    response = client.get('/incomes/edit?id=1', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.get('/incomes/edit?id=1', follow_redirects=True)
    assert response.status_code == 404
    assert b"404" in response.data
    assert response.request.path == '/incomes/edit'

def test_edit_income(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_income(db_setup, users[0])
    income = db_setup.session.scalar(db_setup.select(Income).filter_by(user_id=users[0].id, id=1))
    assert income is not None
    old_id = income.id
    assert income.amount == 50.00
    assert income.category == 'None'
    response = client.post('/incomes/edit?id=1', data={
        'date': '2025-12-01',
        'amount': 75.00,
        'source': 'new location',
        'category': 'Food',
        'description': 'edited'
    }, follow_redirects=True)
    income = db_setup.session.scalar(db_setup.select(Income).filter_by(user_id=users[0].id, id=1))
    assert income is not None
    assert income.source == 'New location'
    assert income.id == old_id
    assert income.amount == 75.00
    assert income.category == 'Food'
    assert b"New location" in response.data
    assert b"None" not in response.data
    assert response.status_code == 200
    assert response.request.path == '/incomes'
    response = client.post('/incomes/edit?id=2', data={}, follow_redirects=True)
    assert response.status_code == 404
    assert response.request.path == '/incomes/edit'
    logout(client)
    response = client.post('/incomes/edit?id=1', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.post('/incomes/edit?id=1', data={}, follow_redirects=True)
    assert b"404" in response.data
    assert response.status_code == 404
    assert response.request.path == '/incomes/edit'

def test_get_delete_income_page(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_income(db_setup, users[0], 2)
    response = client.get('/incomes/delete?id=1', follow_redirects=True)
    assert response.status_code == 200
    assert b"Delete" in response.data
    assert b"Location1" in response.data
    assert response.request.path == '/incomes/delete'
    response = client.get('/incomes/delete?id=3', follow_redirects=True)
    assert response.status_code == 404
    assert b"404" in response.data
    assert response.request.path == '/incomes/delete'
    logout(client)
    response = client.get('/incomes/delete?id=2', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.get('/incomes/delete?id=2', follow_redirects=True)
    assert response.status_code == 404
    assert b"404" in response.data
    assert response.request.path == '/incomes/delete'

def test_delete_income(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_income(db_setup, users[0], 2)
    income = db_setup.session.scalar(db_setup.select(Income).filter_by(user_id=users[0].id, id=1))
    assert income is not None
    response = client.post('/incomes/delete?id=1', data={'id': 1}, follow_redirects=True)
    income = db_setup.session.scalar(db_setup.select(Income).filter_by(user_id=users[0].id, id=1))
    assert income is None
    assert response.status_code == 200
    assert response.request.path == '/incomes'
    response = client.post('/incomes/delete?id=1', data={'id': 1}, follow_redirects=True)
    assert b"404" in response.data
    assert response.status_code == 404
    assert response.request.path == '/incomes/delete'
    logout(client)
    response = client.post('/incomes/delete?id=2', data={'id': 2}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.post('/incomes/delete?id=2', data={'id': 2}, follow_redirects=True)
    assert b"404" in response.data
    assert response.status_code == 404
    assert response.request.path == '/incomes/delete'

def test_filter_incomes(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_income(db_setup, users[0], 6)
    response = client.post('/incomes/filter', data={
        'start_date': None,
        'end_date': '2026-03-01',
        'min_amount': 51.00,
        'max_amount': 53.00,
        'categories': None,
        'source': 'location1, location2, location3, location6'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/incomes'
    assert b"Location1" not in response.data
    assert b"Location2" in response.data
    assert b"Location3" in response.data
    assert b"Location6" not in response.data
    logout(client)
    response = client.post('/incomes/filter', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.post('/incomes/filter', data={
        'start_date': None,
        'end_date': '2026-03-01',
        'min_amount': 51.00,
        'max_amount': 53.00,
        'categories': None,
        'source': 'location1, location2, location3, location6'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/incomes'
    assert b"Location" not in response.data

### Category tests ###

def test_get_categories_page(client, db_setup):
    register_users(db_setup)
    login(client)
    response = client.get('/categories', follow_redirects=True)
    assert response.status_code == 200
    assert b"Your Categories" in response.data
    assert response.request.path == '/categories'
    logout(client)
    response = client.get('/categories', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'

def test_get_add_category_page(client, db_setup):
    register_users(db_setup)
    login(client)
    response = client.get('/categories/add', follow_redirects=True)
    assert response.status_code == 200
    assert b"Add a category" in response.data
    assert response.request.path == '/categories/add'
    logout(client)
    response = client.get('/categories/add', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'

def test_add_category(client, db_setup):
    users = register_users(db_setup)
    login(client)
    response = client.post('/categories/add', data={
        'category': 'Test',
        'description': 'test category',
        'type': 'Expense',
    }, follow_redirects=True)
    category = db_setup.session.scalar(db_setup.select(Category).filter_by(user_id=users[0].id))
    assert category is not None
    assert category.name == 'Test'
    assert category.description == 'test category'
    assert category.type == 'Expense'
    assert b"Test" in response.data
    assert response.status_code == 200
    assert response.request.path == '/categories'
    logout(client)
    response = client.post('/categories/add', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'

def test_add_existing_category(client, db_setup):
    users = register_users(db_setup)
    login(client)
    client.post('/categories/add', data={
        'category': 'Test',
        'description': 'category',
        'type': 'Expense',
    }, follow_redirects=True)
    response = client.post('/categories/add', data={
        'category': 'Test',
        'description': 'category1',
        'type': 'Expense',
    }, follow_redirects=True)
    category = db_setup.session.scalar(db_setup.select(Category).filter_by(user_id=users[0].id, id=1))
    assert category is not None
    assert category.name == 'Test'
    assert category.description == 'category'
    category = db_setup.session.scalar(db_setup.select(Category).filter_by(user_id=users[0].id, id=2))
    assert category is None
    assert b"Test" in response.data
    assert b"category1" not in response.data
    assert response.status_code == 200
    assert response.request.path == '/categories'

def test_get_edit_category_page(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_category(db_setup, users[0])
    response = client.get('/categories/edit?id=1', follow_redirects=True)
    assert response.status_code == 200
    assert b"Edit" in response.data
    assert b"Category1" in response.data
    assert response.request.path == '/categories/edit'
    response = client.get('/categories/edit?id=2', follow_redirects=True)
    assert response.status_code == 404
    assert b"404" in response.data
    assert response.request.path == '/categories/edit'
    logout(client)
    response = client.get('/categories/edit?id=1', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.get('/categories/edit?id=1', follow_redirects=True)
    assert response.status_code == 404
    assert b"404" in response.data
    assert response.request.path == '/categories/edit'

def test_edit_category(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_category(db_setup, users[0])
    category = db_setup.session.scalar(db_setup.select(Category).filter_by(user_id=users[0].id, id=1))
    assert category is not None
    old_id = category.id
    assert category.name == 'Category1'
    assert category.description == ''
    assert category.type == 'Expense'
    response = client.post('/categories/edit?id=1', data={
        'category': 'edited test',
        'description': 'edited',
        'type': 'Income'
    }, follow_redirects=True)
    category = db_setup.session.scalar(db_setup.select(Category).filter_by(user_id=users[0].id, id=1))
    assert category is not None
    assert category.name == 'Edited test'
    assert category.id == old_id
    assert category.description == 'edited'
    assert category.type == 'Income'
    assert b"Edited test" in response.data
    assert b"Category1" not in response.data
    assert response.status_code == 200
    assert response.request.path == '/categories'
    response = client.post('/categories/edit?id=2', data={}, follow_redirects=True)
    assert b"404" in response.data
    assert response.status_code == 404
    assert response.request.path == '/categories/edit'
    logout(client)
    response = client.post('/categories/edit?id=1', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.post('/categories/edit?id=1', data={}, follow_redirects=True)
    assert b"404" in response.data
    assert response.status_code == 404
    assert response.request.path == '/categories/edit'

def test_edit_to_existing_category(client, db_setup):
    users = register_users(db_setup)
    login(client)
    add_category(db_setup, users[0], 2)
    response = client.post('/categories/edit?id=2', data={
        'category': 'Category1',
        'description': 'edited',
        'type': 'Expense'
    }, follow_redirects=True)
    category = db_setup.session.scalar(db_setup.select(Category).filter_by(user_id=users[0].id, id=2))
    assert category is not None
    assert category.name == 'Category2'
    assert category.description == ''
    assert category.type == 'Expense'
    assert b"Category1" in response.data
    assert b"Category2" in response.data
    assert response.status_code == 200
    assert response.request.path == '/categories/edit'

def test_get_delete_category_page(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_category(db_setup, users[0], 2)
    response = client.get('/categories/delete?id=1', follow_redirects=True)
    assert response.status_code == 200
    assert b"Delete" in response.data
    assert b"Category1" in response.data
    assert response.request.path == '/categories/delete'
    response = client.get('/categories/delete?id=3', follow_redirects=True)
    assert response.status_code == 404
    assert b"404" in response.data
    assert response.request.path == '/categories/delete'
    logout(client)
    response = client.get('/categories/delete?id=2', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.get('/categories/delete?id=2', follow_redirects=True)
    assert response.status_code == 404
    assert b"404" in response.data
    assert response.request.path == '/categories/delete'

def test_delete_category(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_category(db_setup, users[0], 2)
    category = db_setup.session.scalar(db_setup.select(Category).filter_by(user_id=users[0].id, id=1))
    assert category is not None
    response = client.post('/categories/delete?id=1', data={'id': 1}, follow_redirects=True)
    category = db_setup.session.scalar(db_setup.select(Category).filter_by(user_id=users[0].id, id=1))
    assert category is None
    assert response.status_code == 200
    assert response.request.path == '/categories'
    response = client.post('/categories/delete?id=1', data={'id': 1}, follow_redirects=True)
    assert b"404" in response.data
    assert response.status_code == 404
    assert response.request.path == '/categories/delete'
    logout(client)
    response = client.post('/categories/delete?id=2', data={'id': 2}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login' 
    login(client, 2)
    response = client.post('/categories/delete?id=2', data={'id': 2}, follow_redirects=True)
    assert b"404" in response.data
    assert response.status_code == 404
    assert response.request.path == '/categories/delete'

### Budget tests ###

def test_get_budgets_page(client, db_setup):
    register_users(db_setup)
    login(client)
    response = client.get('/budget', follow_redirects=True)
    assert response.status_code == 200
    assert b"Your Budget" in response.data
    assert response.request.path == '/budget'
    logout(client)
    response = client.get('/budget', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'

def test_get_add_budget_page(client, db_setup):
    register_users(db_setup)
    login(client)
    response = client.get('/budget/add', follow_redirects=True)
    assert response.status_code == 200
    assert b"Add a budget" in response.data
    assert response.request.path == '/budget/add'
    logout(client)
    response = client.get('/budget/add', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'

def test_add_budget(client, db_setup):
    users = register_users(db_setup)
    login(client)
    response = client.post('/budget/add', data={
        'category': 'Test',
        'amount': 50
    }, follow_redirects=True)
    budget = db_setup.session.scalar(db_setup.select(Budget).filter_by(user_id=users[0].id, id=1))
    assert budget is not None
    assert budget.category == 'Test'
    assert budget.amount == 50
    assert response.status_code == 200
    assert response.request.path == '/budget'
    logout(client)
    response = client.post('/budget/add', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'

def test_add_existing_budget(client, db_setup):
    users = register_users(db_setup)
    login(client)
    add_budget(db_setup, users[0])
    response = client.post('/budget/add', data={
        'category': 'Budget1',
        'amount': 100
    }, follow_redirects=True)
    budget = db_setup.session.scalar(db_setup.select(Budget).filter_by(user_id=users[0].id, id=1))
    assert budget is not None
    assert budget.category == 'Budget1'
    assert budget.amount == 50
    budget = db_setup.session.scalar(db_setup.select(Budget).filter_by(user_id=users[0].id, id=2))
    assert budget is None
    assert b"Budget1" in response.data
    assert response.status_code == 200
    assert response.request.path == '/budget'

def test_get_edit_budget_page(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_budget(db_setup, users[0])
    response = client.get('/budget/edit?id=1', follow_redirects=True)
    assert response.status_code == 200
    assert b"Edit" in response.data
    assert b"Budget1" in response.data
    assert response.request.path == '/budget/edit'
    response = client.get('/budget/edit?id=2', follow_redirects=True)
    assert response.status_code == 404
    assert b"404" in response.data
    assert response.request.path == '/budget/edit'
    logout(client)
    response = client.get('/budget/edit?id=1', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.get('/budget/edit?id=1', follow_redirects=True)
    assert response.status_code == 404
    assert b"404" in response.data
    assert response.request.path == '/budget/edit'

def test_edit_budget(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_budget(db_setup, users[0])
    budget = db_setup.session.scalar(db_setup.select(Budget).filter_by(user_id=users[0].id, id=1))
    assert budget is not None
    old_id = budget.id
    assert budget.category == 'Budget1'
    assert budget.amount == 50
    response = client.post('/budget/edit?id=1', data={
        'category': 'Edited Budget',
        'amount': 100
    }, follow_redirects=True)
    budget = db_setup.session.scalar(db_setup.select(Budget).filter_by(user_id=users[0].id, id=1))
    assert budget is not None
    assert budget.id == old_id
    assert budget.category == 'Edited budget'
    assert budget.amount == 100
    assert b"Edited budget" in response.data
    assert response.status_code == 200
    assert response.request.path == '/budget'
    response = client.post('/budget/edit?id=2', data={}, follow_redirects=True)
    assert b"404" in response.data
    assert response.status_code == 404
    assert response.request.path == '/budget/edit'
    logout(client)
    response = client.post('/budget/edit?id=1', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.post('/budget/edit?id=1', data={}, follow_redirects=True)
    assert b"404" in response.data
    assert response.status_code == 404
    assert response.request.path == '/budget/edit'

def test_edit_to_existing_budget(client, db_setup):
    users = register_users(db_setup)
    login(client)
    add_budget(db_setup, users[0], 2)
    response = client.post('/budget/edit?id=2', data={
        'category': 'Budget1',
        'amount': 200
    }, follow_redirects=True)
    budget = db_setup.session.scalar(db_setup.select(Budget).filter_by(user_id=users[0].id, id=2))
    assert budget is not None
    assert budget.category == 'Budget2'
    assert budget.amount == 51
    assert b"Budget1" in response.data
    assert b"Budget2" in response.data
    assert response.status_code == 200
    assert response.request.path == '/budget/edit'

def test_get_delete_budget_page(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_budget(db_setup, users[0], 2)
    response = client.get('/budget/delete?id=1', follow_redirects=True)
    assert response.status_code == 200
    assert b"Delete" in response.data
    assert b"Budget1" in response.data
    assert response.request.path == '/budget/delete'
    response = client.get('/budget/delete?id=3', follow_redirects=True)
    assert response.status_code == 404
    assert b"404" in response.data
    assert response.request.path == '/budget/delete'
    logout(client)
    response = client.get('/budget/delete?id=2', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.get('/budget/delete?id=2', follow_redirects=True)
    assert response.status_code == 404
    assert b"404" in response.data
    assert response.request.path == '/budget/delete'

def test_delete_budget(client, db_setup):
    users = register_users(db_setup, 2)
    login(client)
    add_budget(db_setup, users[0], 2)
    budget = db_setup.session.scalar(db_setup.select(Budget).filter_by(user_id=users[0].id, id=1))
    assert budget is not None
    response = client.post('/budget/delete?id=1', data={'id': 1}, follow_redirects=True)
    budget = db_setup.session.scalar(db_setup.select(Budget).filter_by(user_id=users[0].id, id=1))
    assert budget is None
    assert response.status_code == 200
    assert response.request.path == '/budget'
    response = client.post('/budget/delete?id=1', data={'id': 1}, follow_redirects=True)
    assert b"404" in response.data
    assert response.status_code == 404
    assert response.request.path == '/budget/delete'
    logout(client)
    response = client.post('/budget/delete?id=2', data={'id': 2}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    login(client, 2)
    response = client.post('/budget/delete?id=2', data={'id': 2}, follow_redirects=True)
    assert b"404" in response.data
    assert response.status_code == 404
    assert response.request.path == '/budget/delete'
