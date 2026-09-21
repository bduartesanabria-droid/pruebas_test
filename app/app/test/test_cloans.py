from datetime import datetime, timedelta
from app.models.cloans import ComputerLoan
from app import db


def test_index_computer_loans(client, computer_loan):
    response = client.get('/cloans/')
    assert response.status_code == 200
    assert b"Lista de" in response.data
    assert str(computer_loan.idLoan).encode('utf-8') in response.data


def test_add_computer_loan_page(client, computer, user):
    response = client.get('/cloans/add')
    assert response.status_code == 200
    assert computer.brandComputer.encode('utf-8') in response.data
    assert user.nameUser.encode('utf-8') in response.data


def test_add_computer_loan(client, computer, user):
    response = client.post('/cloans/add', data={
        'computerId': computer.idComputer,
        'userId': user.idUser,
        'loanDate': datetime.utcnow().strftime('%Y-%m-%dT%H:%M'),
        'status': 'Active'
    }, follow_redirects=True)

    assert response.status_code == 200

    created = ComputerLoan.query.filter_by(computerId=computer.idComputer, userId=user.idUser).first()
    assert created is not None
    assert created.status == 'Active'


def test_update_computer_loan_page(client, computer_loan, computer, user):
    response = client.get(f'/cloans/update/{computer_loan.idLoan}')
    assert response.status_code == 200
    assert computer.brandComputer.encode('utf-8') in response.data


def test_update_computer_loan(client, computer_loan, computer, user):
    loan_date_str = datetime.utcnow().strftime('%Y-%m-%dT%H:%M')
    return_date_str = (datetime.utcnow() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M')

    response = client.post(f'/cloans/update/{computer_loan.idLoan}', data={
        'computerId': computer.idComputer,
        'userId': user.idUser,
        'loanDate': loan_date_str,
        'returnDate': return_date_str,
        'status': 'Extended'
    }, follow_redirects=True)

    assert response.status_code == 200

    db.session.refresh(computer_loan)
    assert computer_loan.status == 'Extended'


def test_return_computer_loan(client, computer_loan):
    response = client.post(f'/cloans/return/{computer_loan.idLoan}', follow_redirects=True)
    assert response.status_code == 200

    db.session.refresh(computer_loan)
    assert computer_loan.status == 'Returned'
    assert computer_loan.returnDate is not None


def test_delete_computer_loan(client, computer_loan):
    loan_id = computer_loan.idLoan
    response = client.post(f'/cloans/delete/{loan_id}', follow_redirects=True)
    assert response.status_code == 200

    deleted = db.session.get(ComputerLoan, loan_id)
    assert deleted is None
