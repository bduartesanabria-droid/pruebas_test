from datetime import datetime, timedelta
from app.models.loans import Loan
from app import db


def test_index_loans(client, loan, book, user):
    response = client.get('/Loan/')
    assert response.status_code == 200
    assert book.titleBook.encode('utf-8') in response.data or user.nameUser.encode('utf-8') in response.data


def test_add_loan_page(client, book, user):
    response = client.get('/Loan/add')
    assert response.status_code == 200
    assert book.titleBook.encode('utf-8') in response.data
    assert user.nameUser.encode('utf-8') in response.data


def test_add_loan(client, book, user):
    response = client.post('/Loan/add', data={
        'bookId': book.idBook,
        'userId': user.idUser
    }, follow_redirects=True)

    assert response.status_code == 200

    created = Loan.query.filter_by(bookId=book.idBook, userId=user.idUser).first()
    assert created is not None
    assert created.status == 'Active'
    assert created.returnDate is not None


def test_edit_loan_page(client, loan):
    response = client.get(f'/Loan/edit/{loan.idLoan}')
    assert response.status_code == 200


def test_edit_loan(client, loan):
    new_return_date = (datetime.now() + timedelta(days=20)).strftime('%Y-%m-%d')
    response = client.post(f'/Loan/edit/{loan.idLoan}', data={
        'returnDate': new_return_date,
        'fine': '5.5',
        'status': 'Overdue'
    }, follow_redirects=True)

    assert response.status_code == 200

    db.session.refresh(loan)
    assert loan.status == 'Overdue'
    assert loan.fine == 5.5


def test_return_loan_on_time(client, loan):
    # Set return date in the future
    loan.returnDate = datetime.now() + timedelta(days=5)
    db.session.commit()

    response = client.get(f'/Loan/return/{loan.idLoan}', follow_redirects=True)
    assert response.status_code == 200

    db.session.refresh(loan)
    assert loan.status == 'Returned'
    assert loan.fine == 0.0


def test_return_loan_late_with_fine(client, loan):
    # Set return date 5 days in the past using local time
    loan.returnDate = datetime.now() - timedelta(days=5)
    db.session.commit()

    response = client.get(f'/Loan/return/{loan.idLoan}', follow_redirects=True)
    assert response.status_code == 200

    db.session.refresh(loan)
    assert loan.status == 'Returned'
    assert loan.fine >= 4.0


def test_delete_loan(client, loan):
    loan_id = loan.idLoan
    response = client.get(f'/Loan/delete/{loan_id}', follow_redirects=True)
    assert response.status_code == 200

    deleted = db.session.get(Loan, loan_id)
    assert deleted is None
