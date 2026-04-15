# Holds all routes related to finances (expenses, incomes, budgets, categories)

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.models import db, Expense, Income, Budget, Category
from flask_login import login_required, current_user
from app.utils import get_all_categories, get_pie_chart, category_in_use
from sqlalchemy import func
from datetime import datetime
import logging

finance_bp = Blueprint('finance', __name__)
logger = logging.getLogger("FinanceLogger")

###
### Expense routes
###


# ------------------------------
@finance_bp.route('/expenses')
@login_required
def expenses():
    logger.debug("Expenses function entered in finance.py")
    query = db.select(Expense).filter_by(user_id=current_user.id)
    expense_filters = session.get('expense_filters', {})
    # Apply filters to the expenses query
    start_str = expense_filters.get('start_date')
    if start_str: # This handles both None and empty string ""
        start = datetime.strptime(start_str, '%Y-%m-%d').date()
        query = query.filter(Expense.date >= start)
    end_str = expense_filters.get('end_date')
    if end_str:
        end = datetime.strptime(end_str, '%Y-%m-%d').date()
        query = query.filter(Expense.date <= end)
    if expense_filters.get('min_amount') is not None:
        query = query.filter(Expense.amount >= expense_filters['min_amount'])
    if expense_filters.get('max_amount') is not None:
        query = query.filter(Expense.amount <= expense_filters['max_amount'])
    if expense_filters.get('categories'):
        lower_categories = [cat.lower() for cat in expense_filters['categories']]
        query = query.filter(func.lower(Expense.category).in_(lower_categories))
    if expense_filters.get('where'):
        lower_places = [place.lower() for place in expense_filters['where']]
        query = query.filter(func.lower(Expense.where).in_(lower_places))

    logger.debug(f"Expenses filtered with current filters")

    # Info about expenses
    total_query = db.select(func.sum(Expense.amount)).where(query.whereclause)
    total = db.session.scalar(total_query) or 0
    avg_query = db.select(func.avg(Expense.amount)).where(query.whereclause)
    avg = db.session.scalar(avg_query) or 0

    query = query.order_by(Expense.date.desc())
    expenses = db.session.scalars(query).all()

    logger.debug("Expenses function exited in finance.py")
    return render_template('expenses.html', expenses=expenses, total=total, avg=round(avg, 2))


#-------------------------------
@finance_bp.route('/expenses/filter', methods=['POST', 'GET'])
@login_required
def filter_expenses():
    logger.debug(f"filter_expenses function entered in finance.py method: {request.method}")

    if request.method == 'POST':

        # Clear previous filters
        session['expense_filters'] = {
            "start_date": None,
            "end_date": None,
            "min_amount": None,
            "max_amount": None,
            "categories": None,
            "where": None
        }
        session['expense_places'] = ""

        if 'clear' in request.form:
            logger.debug("Clearing expense filters as per request")
            return redirect(url_for('finance.filter_expenses'))

        filters = session['expense_filters']
        # Add filters to dictionary
        if request.form.get('start_date'):
            filters['start_date'] = request.form['start_date']
        if request.form.get('end_date'):
            filters['end_date'] = request.form['end_date']
        if request.form.get('min_amount'):
            filters['min_amount'] = float(request.form['min_amount'])
        if request.form.get('max_amount'):
            filters['max_amount'] = float(request.form['max_amount'])

        # Split places & categories
        if request.form.get('where'):
            # Save it to be used as default value
            session['expense_places'] = request.form['where']
            places = [p.strip().capitalize() for p in request.form['where'].split(',') if p.strip()]
            filters['where'] = places
        if request.form.getlist('categories'):
            filters['categories'] = [c.strip() for c in request.form.getlist('categories')]
        
        session.modified = True
        logger.debug(f"filter_expenses (POST) in finance.py applied filters: {filters}")
        return redirect(url_for('finance.expenses'))

    categories = get_all_categories(user_id=current_user.id, type="expense")

    logger.debug(f"filter_expenses in finance.py exited with (GET)")
    return render_template('filter_expenses.html', filters=session.get('expense_filters', {}),
                           places=session.get('expense_places', ''), categories=categories)

#-------------------------------
@finance_bp.route('/expenses/edit', methods=['GET', 'POST'])
@login_required
def edit_expense():
    logger.debug(f"edit_expense function entered in finance.py method: {request.method}")
    expense_id = request.args.get('id')
    expense_to_update = db.one_or_404(
        db.select(Expense).filter_by(id=expense_id, user_id=current_user.id)
    )
    if request.method == 'POST':
        # Process form data and update expense
        date = request.form['date']
        amount = request.form['amount']
        where = request.form['where']
        category = request.form['category']
        description = request.form.get('description')
        # recurring = bool(request.form.get('recurring'))

        # Put date in valid format so SQLite will accept it
        pyDate = datetime.strptime(date, '%Y-%m-%d').date()
        
        if expense_to_update:
            # Update fields
            expense_to_update.date = pyDate
            expense_to_update.amount=amount
            expense_to_update.where=where.capitalize()
            expense_to_update.category=category.capitalize()
            expense_to_update.description=description
            # expense_to_update.recurring=recurring
            
            db.session.commit()
            flash("Expense changed successfully!", "success")
            logger.debug("add_expense function (POST) exited with success in rfinanceoutes.py")
        return redirect(url_for('finance.expenses'))

    categories = get_all_categories(user_id=current_user.id, type="expense")
    logger.debug("edit_expense function exited from GET request in finance.py")
    return render_template('edit_expense.html', expense=expense_to_update, categories=categories)


# ------------------------------
@finance_bp.route('/expenses/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    logger.debug(f"add_expense function entered in finance.py method: {request.method}")
    if request.method == 'POST':
        logger.info(f"Adding expense for user: {current_user.nickname}")
        date = request.form['date']
        amount = request.form['amount']
        where = request.form['where'].capitalize()
        category = request.form['category'].capitalize()
        description = request.form.get('description')
        # recurring = bool(request.form.get('recurring'))

        # Put date in valid format so SQLite will accept it
        pyDate = datetime.strptime(date, '%Y-%m-%d').date()

        expense = Expense(date=pyDate, amount=amount, where=where, category=category,
                          description=description, recurring=False, user_id=current_user.id)
        db.session.add(expense)
        db.session.commit()
        flash("Expense added successfully!", "success")
        logger.debug("add_expense function (POST) exited with success in finance.py")
        return redirect(url_for('finance.expenses'))
    
    categories = get_all_categories(user_id=current_user.id, type="expense")
    logger.debug("add_expense function exited from GET request in finance.py")
    return render_template('add_expense.html', categories=categories)


# ------------------------------
@finance_bp.route('/expenses/delete', methods=['GET', 'POST'])
@login_required
def delete_expense():
    logger.debug(f"delete_expense function entered in finance.py method: {request.method}")
    expense_id = request.args.get('id')
    if request.method == 'POST':
        expense_id = request.form.get('id')
        expense_to_delete = db.one_or_404(
            db.select(Expense).filter_by(id=expense_id, user_id=current_user.id)
        )
        if expense_to_delete:
            db.session.delete(expense_to_delete)
            db.session.commit()
            flash("Expense deleted successfully!", "success")
            logger.debug("delete_expense function (POST) exited with success in finance.py")
        return redirect(url_for('finance.expenses'))
    
    expense = db.one_or_404(
        db.select(Expense).filter_by(id=expense_id, user_id=current_user.id)
    )
    to_see = f"At {expense.where} on {expense.date}"
    logger.debug("delete_expense function exited from GET request in finance.py")
    return render_template('delete.html', cancel_location='expenses', to_see=to_see, type='expense', id=expense_id)


###
### Income routes    
###


# ------------------------------
@finance_bp.route('/incomes')
@login_required
def incomes():
    logger.debug("Incomes function entered in finance.py")
    query = db.select(Income).filter_by(user_id=current_user.id)
    filters = session.get('income_filters', {})
    # Apply filters to the incomes query
    start_str = filters.get('start_date')
    if start_str: 
        start = datetime.strptime(start_str, '%Y-%m-%d').date()
        query = query.filter(Income.date >= start)
    end_str = filters.get('end_date')
    if end_str:
        end = datetime.strptime(end_str, '%Y-%m-%d').date()
        query = query.filter(Income.date <= end)
    if filters.get('min_amount') is not None:
        query = query.filter(Income.amount >= filters['min_amount'])
    if filters.get('max_amount') is not None:
        query = query.filter(Income.amount <= filters['max_amount'])
    if filters.get('categories'):
        lower_categories = [cat.lower() for cat in filters['categories']]
        query = query.filter(func.lower(Income.category).in_(lower_categories))
    if filters.get('where'):
        lower_places = [place.lower() for place in filters['where']]
        query = query.filter(func.lower(Income.where).in_(lower_places))

    logger.debug(f"Incomes filtered with current filters: {filters}")

    # Info about incomes
    total_query = db.select(func.sum(Income.amount)).where(query.whereclause)
    total = db.session.scalar(total_query) or 0
    avg_query = db.select(func.avg(Income.amount)).where(query.whereclause)
    avg = db.session.scalar(avg_query) or 0

    query = query.order_by(Income.date.desc())
    incomes = db.session.scalars(query).all()

    logger.debug("Incomes function exited in finance.py")
    return render_template('incomes.html', incomes=incomes, total=total, avg=round(avg, 2))


#-------------------------------
@finance_bp.route('/incomes/filter', methods=['POST', 'GET'])
@login_required
def filter_incomes():
    logger.debug(f"filter_incomes function entered in finance.py method: {request.method}")

    if request.method == 'POST':

        # Clear previous filters
        session['income_filters'] = {
            "start_date": None,
            "end_date": None,
            "min_amount": None,
            "max_amount": None,
            "categories": None,
            "where": None
        }
        session['income_sources'] = ""

        if 'clear' in request.form:
            logger.debug("Clearing income filters as per request")
            return redirect(url_for('finance.filter_incomes'))

        filters = session['income_filters']
        # Add filters to dictionary
        if request.form.get('start_date'):
            filters['start_date'] = request.form['start_date']
        if request.form.get('end_date'):
            filters['end_date'] = request.form['end_date']
        if request.form.get('min_amount'):
            filters['min_amount'] = float(request.form['min_amount'])
        if request.form.get('max_amount'):
            filters['max_amount'] = float(request.form['max_amount'])

        # Split places & categories
        if request.form.get('source'):
            # Save it to be used as default value
            session['income_sources'] = request.form['source']
            places = [p.strip().capitalize() for p in request.form['source'].split(',') if p.strip()]
            filters['source'] = places
        if request.form.getlist('categories'):
            filters['categories'] = [c.strip() for c in request.form.getlist('categories')]

        session.modified = True
        logger.debug(f"filter_incomes (POST) in finance.py applied filters: {filters}")
        return redirect(url_for('finance.incomes'))

    categories = get_all_categories(user_id=current_user.id, type="income")
    logger.debug(f"filter_incomes in finance.py exited with (GET)")
    return render_template('filter_incomes.html', filters=session.get('income_filters', {}),
                           places=session.get('income_sources', ''), categories=categories)


#-------------------------------
@finance_bp.route('/incomes/edit', methods=['GET', 'POST'])
@login_required
def edit_income():
    logger.debug(f"edit_income function entered in finance.py method: {request.method}")
    income_id = request.args.get('id')
    income_to_update = db.one_or_404(
        db.select(Income).filter_by(id=income_id, user_id=current_user.id)
    )  
    if request.method == 'POST':

        # Process form data and update income
        date = request.form['date']
        amount = request.form['amount']
        source = request.form['source']
        category = request.form['category']
        description = request.form.get('description')
        # recurring = bool(request.form.get('recurring'))

        # Put date in valid format so SQLite will accept it
        pyDate = datetime.strptime(date, '%Y-%m-%d').date()
      
        if income_to_update:
            # Update fields
            income_to_update.date = pyDate
            income_to_update.amount = amount
            income_to_update.source = source.capitalize()
            income_to_update.category = category
            income_to_update.description = description
            # income_to_update.recurring=recurring
            db.session.commit()
            flash("Income changed successfully!", "success")
            logger.debug("add_income function (POST) exited with success in finance.py")
        return redirect(url_for('finance.incomes'))
    
    categories = get_all_categories(user_id=current_user.id, type="income")
    logger.debug("edit_income function exited from GET request in finance.py")
    return render_template('edit_income.html', income=income_to_update, categories=categories)


# ------------------------------
@finance_bp.route('/incomes/add', methods=['GET', 'POST'])
@login_required
def add_income():
    logger.debug(f"add_income function entered in finance.py method: {request.method}")
    if request.method == 'POST':
        logger.info(f"Adding income for user: {current_user.nickname}")
        date = request.form['date']
        amount = request.form['amount']
        category = request.form['category']
        source = request.form['source']
        description = request.form.get('description')
        # recurring = bool(request.form.get('recurring'))

        # Put date in valid format so SQLite will accept it
        pyDate = datetime.strptime(date, '%Y-%m-%d').date()

        income = Income(date=pyDate, amount=amount, source=source.capitalize(),
                        description=description, category=category, recurring=False, user_id=current_user.id)
        db.session.add(income)
        db.session.commit()
        flash("Income added successfully!", "success")
        logger.info(f"Income added successfully for user: {current_user.nickname}")
        logger.debug("add_income function exited with success in finance.py")
        return redirect(url_for('finance.incomes'))
    
    categories = get_all_categories(user_id=current_user.id, type="income")
    logger.debug("add_income function exited from GET request in finance.py")
    return render_template('add_income.html', categories=categories)

    
# ------------------------------
@finance_bp.route('/incomes/delete', methods=['GET', 'POST'])
@login_required
def delete_income():
    logger.debug(f"delete_income function entered in finance.py method: {request.method}")
    income_id = request.args.get('id')

    if request.method == 'POST':
        income_id = request.form.get('id')
        income_to_delete = db.one_or_404(
            db.select(Income).filter_by(id=income_id, user_id=current_user.id)
        )
        if income_to_delete:
            db.session.delete(income_to_delete)
            db.session.commit()
            flash("Income deleted successfully!", "success")
            logger.info(f"Income deleted successfully for user: {current_user.nickname}")
            logger.debug("delete_income function exited with success in finance.py")
        return redirect(url_for('finance.incomes'))
    
    income = db.one_or_404(
        db.select(Income).filter_by(id=income_id, user_id=current_user.id)
    )
    to_see = f"From {income.source} on {income.date}"
    logger.debug(f"delete_income function exited in finance.py from GET method")
    return render_template('delete.html', cancel_location='incomes', to_see=to_see, type='income', id=income_id)


###
### Budget routes
###


#-------------------------------
@finance_bp.route('/budget')
@login_required
def budget():
    logger.debug("budget function entered in finance.py")
    stmt = db.select(Budget).filter_by(user_id=current_user.id)
    total = db.session.scalar(db.select(func.sum(Budget.amount)).filter_by(user_id=current_user.id)) or 0
    budgets_list = db.session.scalars(stmt.order_by(Budget.amount.desc())).all() 
    budget_chart = get_pie_chart(query_data=budgets_list, type="Budgets")
    logger.debug("budget function exited in finance.py")
    return render_template('budget.html', budgets=budgets_list, total=total, budget_chart=budget_chart)


#-------------------------------
@finance_bp.route('/budget/edit', methods=['GET', 'POST'])
@login_required
def edit_budget():
    logger.debug(f"edit_budget function entered in finance.py method: {request.method}")
    budget_id = request.args.get('id')
    budget_to_update = db.one_or_404(
        db.select(Budget).filter_by(id=budget_id, user_id=current_user.id)
    )
    if request.method == 'POST':
        # Process form data and update budget
        new_amount = request.form['amount']
        new_category = request.form['category'].capitalize()
        
        if budget_to_update:
            # Check for a budget with this category already
            existing_budget = db.session.scalar(db.select(Budget).filter_by(category=new_category, 
                                                user_id=current_user.id).filter(Budget.id != budget_to_update.id))
            
            if existing_budget:
                logger.info(f"Budget for {new_category} already existes for user {current_user.nickname}")
                flash(f"Budget already exists for {new_category}", "warning")
                logger.debug(f"existing: {existing_budget.id} new: {budget_to_update.id}")
                categories = get_all_categories(user_id=current_user.id, type="expense")
                logger.info("edit_budget (POST) exited with failure in finance.py")
                return render_template('edit_budget.html', budget=budget_to_update, categories=categories)
            
            # Update fields
            budget_to_update.amount=new_amount
            budget_to_update.category=new_category
            
            db.session.commit()
            flash("Budget changed successfully!", "success")
            logger.debug("edit_budget function (POST) exited with success in finance.py")  
        else:
            flash("Budget not found!", "failure")
            logger.warning(f"edit_budget function (POST) exited with failure in finance.py for Budget ID: {budget_id}")
        return redirect(url_for('finance.budget'))
    
    categories = get_all_categories(user_id=current_user.id, type="expense")
    logger.debug("edit_budget function exited from GET request in finance.py")
    return render_template('edit_budget.html', budget=budget_to_update, categories=categories)


# ------------------------------
@finance_bp.route('/budget/add', methods=['GET', 'POST'])
@login_required
def add_budget():
    logger.debug(f"add_budget function entered in finance.py method: {request.method}")

    if request.method == 'POST':
        logger.info(f"Adding budget for user: {current_user.nickname}")

        new_amount = request.form['amount']
        new_category = request.form['category'].capitalize()

        # Check if category already has a budget
        existing_budget = db.session.scalar(db.select(Budget).filter_by(category=new_category, user_id=current_user.id))
        
        if existing_budget:
            logger.info(f"Budget for {new_category} already existes for user {current_user.nickname}")
            flash(f"Budget already exists for {new_category}. Edit it instead.", "warning")
            logger.debug(f"existing: {existing_budget.id}")
            categories = get_all_categories(user_id=current_user.id, type="expense")
            logger.info("add_budget (POST) exited with failure in finance.py")
            return redirect(url_for('finance.budget'))

        # Add the budget to db
        budget = Budget(amount=new_amount, category=new_category, user_id=current_user.id)
        db.session.add(budget)
        db.session.commit()
        flash("Budget added successfully!", "success")
        logger.info(f"Budget added successfully for user: {current_user.nickname}")
        logger.debug("add_budget function exited with success in finance.py")
        return redirect(url_for('finance.budget'))

    categories = get_all_categories(user_id=current_user.id, type="expense")
    logger.debug("add_budget function exited from GET request in finance.py")
    return render_template('add_budget.html', categories=categories)


#-------------------------------
@finance_bp.route('/budget/delete', methods=['GET', 'POST'])
@login_required
def delete_budget():
    logger.debug(f"delete_budget function entered in finance.py method: {request.method}")
    budget_id = request.args.get('id')
    if request.method == 'POST':
        budget_id = request.form.get('id')
        budget_to_delete = db.one_or_404(
            db.select(Budget).filter_by(id=budget_id, user_id=current_user.id)
        )
        if budget_to_delete:
            db.session.delete(budget_to_delete)
            db.session.commit()
            flash("Budget deleted successfully!", "success")
            logger.info(f"Budget deleted successfully for user: {current_user.nickname}")
            logger.debug("delete_budget function exited with success in finance.py")
        return redirect(url_for('finance.budget'))
    
    budget = db.one_or_404(
        db.select(Budget).filter_by(id=budget_id, user_id=current_user.id)
    )
    logger.debug("delete_budget function exited from GET request in finance.py")
    return render_template('delete.html', cancel_location='budget', to_see=budget.category, type='budget', id=budget_id)


###
### Category Routes
###


#-------------------------------
@finance_bp.route('/categories', methods=['GET'])
@login_required
def categories():
    logger.debug("Categories function entered in finance.py")
    type_requested = request.args.get('types')
    categories = get_all_categories(user_id=current_user.id, type=type_requested)
    logger.debug("Categories function exited in finance.py")
    return render_template('categories.html', categories=categories)


#-------------------------------
@finance_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    logger.debug(f"add_category function entered in finance.py method: {request.method}")

    if request.method == 'POST':
        new_category = request.form['category'].strip().capitalize()  
        description = request.form['description']
        type = request.form['type']

        # Check if the category exists already for this user
        exists = db.session.scalar(db.select(Category).filter_by(name=new_category, user_id=current_user.id, type=type.capitalize()))
        
        if exists:
            logger.info(f"Category '{new_category}' already exists for this type for user: {current_user.nickname}")
            flash(f"Category '{new_category}' already exists for this type!", "info")
            logger.debug("add_category function exited with failure in finance.py")
        else:
            # Add it to db
            category = Category(name=new_category, description=description, type=type.capitalize(), user_id=current_user.id)
            db.session.add(category)
            db.session.commit()
            flash(f"Category '{category.name}' added successfully!", "success")
            logger.info(f"Category '{category.name}' added by user: {current_user.nickname}")
            logger.debug("add_category function exited in finance.py")

        return redirect(url_for('finance.categories'))

    logger.debug("add_category function exited from GET request in finance.py")
    return render_template('add_category.html')


#-------------------------------
@finance_bp.route('/categories/edit', methods=['GET', 'POST'])
@login_required
def edit_category():
    logger.debug(f"edit_category function entered in finance.py method: {request.method}")
    category_id = request.args.get('id')
    category = db.one_or_404(
        db.select(Category).filter_by(id=category_id, user_id=current_user.id)
    )
    if request.method == 'POST':
        new_name = request.form['category'].strip().capitalize()
        new_description = request.form['description']
        new_type = request.form['type'].capitalize()
        
        # Check if the new name/type combination already exists
        existing_category = db.session.scalar(db.select(Category).filter(Category.name==new_name, Category.type==new_type, Category.user_id==current_user.id, Category.id != category_id))
        if existing_category:
            logger.warning(f"Category '{new_name}' already exists for {new_type} for user: {current_user.nickname}")
            flash(f"Category '{new_name}' already exists for this type!", "info")
            logger.debug("edit_category function exited with failure (existing name) in finance.py")
            return render_template('edit_category.html', category=category)
        
        # When changing type or name, check for existing expenses / incomes using this category
        if new_type != category.type or new_name != category.name:
            in_use = category_in_use(category, current_user.id)
            if in_use:
                logger.warning(f"Can't change type of '{category.name}' because in use for: {current_user.nickname}")
                flash("Can't change category because it's in use!", "warning")
                logger.debug("edit_category function exited with failure (type in use) in finance.py")
                return redirect(url_for('finance.categories'))

        # Update database
        category.name = new_name
        category.description = new_description
        category.type = new_type
        db.session.commit()
        flash(f"Changed category '{category.name}'", "success")
        logger.info(f"Category '{category.id}' updated by user: {current_user.nickname}")
        logger.debug("edit_category function exited with success in finance.py")
        return redirect(url_for('finance.categories'))

    logger.debug("edit_category function exited from GET request in finance.py")
    return render_template('edit_category.html', category=category)


#-------------------------------
@finance_bp.route('/categories/delete', methods=['GET', 'POST'])
@login_required
def delete_category():
    logger.debug(f"delete_category function entered in finance.py method: {request.method}")
    category_id = request.args.get('id')

    if request.method == 'POST':
        category_id = request.form.get('id')
        to_delete = db.one_or_404(
            db.select(Category).filter_by(id=category_id, user_id=current_user.id)
        )

        # Check if the category is being used
        in_use = category_in_use(to_delete, current_user.id)
        if in_use:
            logger.warning(f"Can't delete '{to_delete.name}' because in use for: {current_user.nickname}")
            flash("Can't delete, category in use!", "warning")
            logger.debug("delete_category function (POST) exited with unable in finance.py")
            return redirect(url_for('finance.categories'))

        # Update db
        db.session.delete(to_delete)
        db.session.commit()
        flash(f"Deleted category '{to_delete.name}'", "success")
        logger.info(f"Category '{to_delete.name}' deleted by user: {current_user.nickname}")
        logger.debug("delete_category function (POST) exited with success in finance.py")
        return redirect(url_for('finance.categories'))

    to_delete = db.one_or_404(
        db.select(Category).filter_by(id=category_id, user_id=current_user.id)
    )    
    logger.debug("delete_category function exited from GET request with success in finance.py")
    return render_template('delete.html', cancel_location='categories', to_see=to_delete.name, type='category', id=category_id)