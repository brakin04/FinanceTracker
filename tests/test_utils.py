from test_finance import add_budget, add_category, add_expense, add_income
from test_auth import login, logout, register_users
from app.utils import get_file_content, get_all_categories, get_finances_by_date_range, get_total_from_query_list
from datetime import datetime
import os

def test_get_file_content():
    content = get_file_content(os.getcwd() + '/tests/test_utils.py')
    assert "test_get_file_content" in content

def test_get_all_categories(client, db_setup):
    users = register_users(db_setup)
    login(client)
    add_category(db_setup, users[0], 5, 'e')
    add_category(db_setup, users[0], 4, 'i')
    exp_cats = get_all_categories(user_id=users[0].id, type="Expense")
    inc_cats = get_all_categories(user_id=users[0].id, type="Income")
    all_cats = get_all_categories(user_id=users[0].id)
    assert len(exp_cats) == 5
    assert len(inc_cats) == 4
    assert len(all_cats) == 9

def test_get_fin_by_date_range(client, db_setup):
    users = register_users(db_setup)
    login(client)
    add_expense(db_setup, users[0], 5)
    add_income(db_setup, users[0], 5)
    start = datetime.strptime('2025-12-02', '%Y-%m-%d').date()
    end = datetime.strptime('2025-12-04', '%Y-%m-%d').date()
    inc_by_date = get_finances_by_date_range(user_id=users[0].id, start_date=start, end_date=end, finance_type='i')
    exp_by_date = get_finances_by_date_range(user_id=users[0].id, start_date=start, end_date=end, finance_type='e')
    none_by_date = get_finances_by_date_range(user_id=users[0].id, start_date=start, end_date=end)
    assert len(inc_by_date) == 3
    for inc in inc_by_date:
        assert inc.date <= end
        assert inc.date >= start
    assert len(exp_by_date) == 3
    for exp in exp_by_date:
        assert exp.date <= end
        assert exp.date >= start
    assert none_by_date is None

def test_get_total_from_query_list(client, db_setup):
    users = register_users(db_setup)
    login(client)
    add_expense(db_setup, users[0], 5)
    add_income(db_setup, users[0], 5)
    inc_by_date = get_finances_by_date_range(user_id=users[0].id, finance_type='i')
    exp_by_date = get_finances_by_date_range(user_id=users[0].id, finance_type='e')
    none_by_date = get_finances_by_date_range(user_id=users[0].id)
    inc_sum = get_total_from_query_list(inc_by_date)
    exp_sum = get_total_from_query_list(exp_by_date)
    none_sum = get_total_from_query_list(none_by_date)
    assert inc_sum == 260
    assert exp_sum == 260
    assert none_sum == 0
