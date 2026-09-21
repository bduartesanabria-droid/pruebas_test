import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models.users import User
from app.models.authors import Author
from app.models.books import Book
from app.models.computers import Computer
from app.models.rooms import Room
from app.models.loans import Loan
from app.models.cloans import ComputerLoan


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    test_user = User(nameUser="test_user", passwordUser="test_password")
    db.session.add(test_user)
    db.session.commit()
    return test_user


@pytest.fixture
def authenticated_client(client, user):
    with client.session_transaction() as session:
        session['_user_id'] = str(user.idUser)
        session['_fresh'] = True
    return client


@pytest.fixture
def author(app):
    test_author = Author(nameAuthor="Gabriel Garcia Marquez", nationalityAuthor="Colombian")
    db.session.add(test_author)
    db.session.commit()
    return test_author


@pytest.fixture
def book(app, author):
    test_book = Book(titleBook="Cien Anos de Soledad", authorId=author.idAuthor)
    db.session.add(test_book)
    db.session.commit()
    return test_book


@pytest.fixture
def computer(app):
    test_computer = Computer(brandComputer="Dell", modelComputer="Latitude 5420", statusComputer="Active")
    db.session.add(test_computer)
    db.session.commit()
    return test_computer


@pytest.fixture
def room(app):
    test_room = Room(name="Sala de Lectura A", description="Sala silenciosa para estudio individual")
    db.session.add(test_room)
    db.session.commit()
    return test_room


@pytest.fixture
def loan(app, book, user):
    test_loan = Loan(
        bookId=book.idBook,
        userId=user.idUser,
        loanDate=datetime.utcnow(),
        returnDate=datetime.utcnow() + timedelta(days=14),
        fine=0.0,
        status="Active"
    )
    db.session.add(test_loan)
    db.session.commit()
    return test_loan


@pytest.fixture
def computer_loan(app, computer, user):
    test_cloan = ComputerLoan(
        computerId=computer.idComputer,
        userId=user.idUser,
        loanDate=datetime.utcnow(),
        returnDate=None,
        status="Active"
    )
    db.session.add(test_cloan)
    db.session.commit()
    return test_cloan