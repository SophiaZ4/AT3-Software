from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Question, Choice, QuizResult
from . import db

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/quiz', methods=['GET', 'POST'])
@login_required
def take_quiz():
    # Logic for handling quiz submission
    if request.method == 'POST':
        # Get all questions to calculate score
        questions = Question.query.all()
        score = 0
        total = len(questions)

        # Iterate through questions to check answers
        for question in questions:
            submitted_choice_id = request.form.get(f'question_{question.id}')
            if submitted_choice_id:
                submitted_choice = Choice.query.get(submitted_choice_id)
                if submitted_choice and submitted_choice.is_correct:
                    score += 1
        
        # Save the result to the database
        new_result = QuizResult(
            score=score, 
            total_questions=total, 
            user_id=current_user.id
        )
        db.session.add(new_result)
        db.session.commit()
        
        flash(f'Quiz submitted! Your score is {score}/{total}.', 'success')
        return redirect(url_for('quiz.take_quiz')) # Redirect to the same page to show results

    # Logic for displaying the page (GET request)
    
    # Check if user wants to retry
    retry = request.args.get('retry', 'false').lower() == 'true'

    # Find the most recent quiz result for the current user
    last_result = QuizResult.query.filter_by(user_id=current_user.id).order_by(QuizResult.timestamp.desc()).first()

    # If the user has a past result and not retrying, show the result page
    if last_result and not retry:
        return render_template('quiz_result.html', result=last_result)

    # Otherwise (no past result OR are retrying), show the quiz questions
    questions = Question.query.all()
    if not questions:
        flash('No quiz questions have been set up yet. Please contact an admin.', 'warning')
        return render_template('quiz.html', questions=[])
        
    return render_template('quiz.html', questions=questions)