from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
import bleach
from . import db
from .models import User, Question, Choice

auth = Blueprint('auth', __name__)

@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        # User is already logged in, send them to the main page
        return redirect(url_for('index')) # Redirect to the main index page
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            # Redirect to the page the user was trying to access, or to the index
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    
    return render_template('auth/login.html') # return back to login page if unauthorised

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = bleach.clean(request.form.get('username'))
        password = request.form.get('password')
        existing_user = User.query.filter_by(username=username).first()

        if existing_user is None:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('auth.signin'))
        else:
            flash('That username is already taken. Please choose a different one.', 'danger')

    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.signin'))

# --- Add this code to the bottom of auth.py ---

@auth.route('/admin')
@login_required
def admin_dashboard():
    # First, check if the logged-in user is actually an admin
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))

    # Fetch all users AND all questions
    all_users = User.query.all()
    all_questions = Question.query.order_by(Question.id).all()
    
    # Pass both lists to the template
    return render_template('admin.html', users=all_users, questions=all_questions)

@auth.route('/admin/question/add', methods=['GET', 'POST'])
@login_required
def add_question():
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('auth.admin_dashboard'))

    if request.method == 'POST':
        question_text = bleach.clean(request.form.get('question_text'))
        choices_text = [bleach.clean(text) for text in request.form.getlist('choices')] # Gets a list of all choice inputs
        correct_choice_index = int(request.form.get('correct_choice')) - 1 # (1-4) -> (0-3)

        if not question_text or len(choices_text) != 4 or '' in choices_text:
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('auth.add_question'))

        # Create the new question
        new_question = Question(text=question_text)
        db.session.add(new_question)

        # Create the new choices
        for i, choice_text in enumerate(choices_text):
            is_correct = (i == correct_choice_index)
            choice = Choice(text=choice_text, is_correct=is_correct, question=new_question)
            db.session.add(choice)
        
        db.session.commit()
        flash('New question added successfully!', 'success')
        return redirect(url_for('auth.admin_dashboard'))

    return render_template('add_question.html')

@auth.route('/admin/question/edit/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('auth.admin_dashboard'))
    
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        question.text = bleach.clean(request.form.get('question_text'))
        correct_choice_id = int(request.form.get('correct_choice_id'))

        # Update each choice
        for choice in question.choices:
            choice.text = bleach.clean(request.form.get(f'choice_text_{choice.id}'))
            choice.is_correct = (choice.id == correct_choice_id)
            
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('auth.admin_dashboard'))

    return render_template('edit_question.html', question=question)

@auth.route('/admin/question/delete/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('auth.admin_dashboard'))
        
    question = Question.query.get_or_404(question_id)
    
    # Because of the 'cascade' option in our models,
    # deleting the question will automatically delete its choices.
    db.session.delete(question)
    db.session.commit()
    
    flash('Question has been deleted.', 'success')
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('auth.admin_dashboard'))

    user_to_edit = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # Sanitize username input
        new_username = bleach.clean(request.form.get('username'))
        
        # Check if the new username is already taken by another user
        existing_user = User.query.filter(User.username == new_username, User.id != user_id).first()
        if existing_user:
            flash('That username is already taken. Please choose another.', 'danger')
            return render_template('edit_user.html', user=user_to_edit)

        # Update username and admin status
        user_to_edit.username = new_username
        user_to_edit.is_admin = True if request.form.get('is_admin') else False
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('auth.admin_dashboard'))

    return render_template('edit_user.html', user=user_to_edit)


@auth.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('auth.admin_dashboard'))
    
    # CRITICAL: Prevent an admin from deleting their own account
    if user_id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('auth.admin_dashboard'))

    user_to_delete = User.query.get_or_404(user_id)
    
    db.session.delete(user_to_delete)
    db.session.commit()
    
    flash(f'User {user_to_delete.username} has been deleted.', 'success')
    return redirect(url_for('auth.admin_dashboard'))