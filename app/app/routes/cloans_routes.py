from flask import Blueprint, request, render_template, redirect, url_for
from app import db
from app.models.cloans import ComputerLoan
from app.models.computers import Computer
from app.models.users import User
from datetime import datetime

bp = Blueprint('cloans', __name__, url_prefix='/cloans')


@bp.route('/', methods=['GET'])
def index():
    loans = ComputerLoan.query.all()
    return render_template('cloans/index.html', loans=loans)

@bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        computerId = request.form['computerId']
        userId = request.form['userId']
        loanDate_raw = request.form.get('loanDate')
        returnDate_raw = request.form.get('returnDate')
        
        try:
            loanDate = datetime.fromisoformat(loanDate_raw) if loanDate_raw else datetime.utcnow()
        except Exception:
            loanDate = datetime.utcnow()
            
        try:
            returnDate = datetime.fromisoformat(returnDate_raw) if returnDate_raw else None
        except Exception:
            returnDate = None

        status = request.form.get('status', 'Active')
        
        new_loan = ComputerLoan(
            computerId=computerId,
            userId=userId,
            loanDate=loanDate,
            returnDate=returnDate,
            status=status
        )
        db.session.add(new_loan)
        db.session.commit()
        return redirect(url_for('cloans.index'))
    
    computers = Computer.query.all()
    users = User.query.all()
    return render_template('cloans/add.html', computers=computers, users=users)

@bp.route('/update/<int:id>', methods=['GET', 'POST'])
def edit(id):
    loan = ComputerLoan.query.get_or_404(id)
    if request.method == 'POST':
        loan.computerId = request.form['computerId']
        loan.userId = request.form['userId']
        
        loanDate_raw = request.form.get('loanDate')
        returnDate_raw = request.form.get('returnDate')
        
        if loanDate_raw:
            try:
                loan.loanDate = datetime.fromisoformat(loanDate_raw)
            except Exception:
                pass
                
        if returnDate_raw:
            try:
                loan.returnDate = datetime.fromisoformat(returnDate_raw)
            except Exception:
                loan.returnDate = None
        else:
            loan.returnDate = None

        loan.status = request.form.get('status', loan.status)
        db.session.commit()
        return redirect(url_for('cloans.index'))
    
    computers = Computer.query.all()
    users = User.query.all()
    return render_template('cloans/edit.html', loan=loan, computers=computers, users=users)

@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    loan = ComputerLoan.query.get_or_404(id)
    db.session.delete(loan)
    db.session.commit()
    return redirect(url_for('cloans.index'))

@bp.route('/return/<int:id>', methods=['POST'])
def return_computer(id):
    loan = ComputerLoan.query.get_or_404(id)
    loan.status = 'Returned'
    loan.returnDate = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('cloans.index'))
