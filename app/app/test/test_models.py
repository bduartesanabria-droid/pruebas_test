import base64
from datetime import datetime, timedelta
from app import db
from app.models.users import User
from app.models.authors import Author
from app.models.books import Book
from app.models.computers import Computer
from app.models.rooms import Room
from app.models.loans import Loan
from app.models.cloans import ComputerLoan


def test_user_model(app):
    user = User(nameUser="alice", passwordUser="password123")
    db.session.add(user)
    db.session.commit()

    assert user.idUser is not None
    assert user.nameUser == "alice"
    assert user.passwordUser == "password123"
    assert user.get_id() == str(user.idUser)


def test_user_generate_qr(app, user):
    qr_b64 = user.generate_qr()
    assert qr_b64 is not None
    assert isinstance(qr_b64, str)
    # Validate base64 decode
    decoded = base64.b64decode(qr_b64)
    assert len(decoded) > 0
    # PNG signature check: \x89PNG\r\n\x1a\n
    assert decoded.startswith(b'\x89PNG\r\n\x1a\n')


def test_author_model(app):
    author = Author(nameAuthor="Jorge Luis Borges", nationalityAuthor="Argentinian")
    db.session.add(author)
    db.session.commit()

    assert author.idAuthor is not None
    assert author.nameAuthor == "Jorge Luis Borges"
    assert author.nationalityAuthor == "Argentinian"
    assert repr(author) == "<Author Jorge Luis Borges>"


def test_book_model(app, author):
    book = Book(titleBook="Ficciones", authorId=author.idAuthor)
    db.session.add(book)
    db.session.commit()

    assert book.idBook is not None
    assert book.titleBook == "Ficciones"
    assert book.authorId == author.idAuthor
    assert book.author.nameAuthor == author.nameAuthor
    assert repr(book) == "<Book Ficciones>"
    assert book in author.books.all()


def test_computer_model(app):
    comp = Computer(brandComputer="Lenovo", modelComputer="ThinkPad X1", statusComputer="Active")
    db.session.add(comp)
    db.session.commit()

    assert comp.idComputer is not None
    assert comp.brandComputer == "Lenovo"
    assert comp.modelComputer == "ThinkPad X1"
    assert comp.statusComputer == "Active"
    assert repr(comp) == f"<Computer {comp.idComputer} - Lenovo ThinkPad X1>"


def test_room_model(app):
    room = Room(name="Sala B", description="Sala de Conferencias")
    db.session.add(room)
    db.session.commit()

    assert room.id is not None
    assert room.name == "Sala B"
    assert room.description == "Sala de Conferencias"
    assert repr(room) == f"<Room {room.id} - Sala B>"


def test_loan_model(app, book, user):
    loan_date = datetime.utcnow()
    return_date = loan_date + timedelta(days=14)
    loan = Loan(
        bookId=book.idBook,
        userId=user.idUser,
        loanDate=loan_date,
        returnDate=return_date,
        fine=0.0,
        status="Active"
    )
    db.session.add(loan)
    db.session.commit()

    assert loan.idLoan is not None
    assert loan.bookId == book.idBook
    assert loan.userId == user.idUser
    assert loan.book.titleBook == book.titleBook
    assert loan.user.nameUser == user.nameUser
    assert repr(loan) == f"<Loan {loan.idLoan} of Book {book.idBook} to User {user.idUser}>"
    assert loan in user.loansUser.all()


def test_computer_loan_model(app, computer, user):
    cloan = ComputerLoan(
        computerId=computer.idComputer,
        userId=user.idUser,
        loanDate=datetime.utcnow(),
        status="Active"
    )
    db.session.add(cloan)
    db.session.commit()

    assert cloan.idLoan is not None
    assert cloan.computerId == computer.idComputer
    assert cloan.userId == user.idUser
    assert cloan.computer.brandComputer == computer.brandComputer
    assert cloan.user.nameUser == user.nameUser
    assert repr(cloan) == f"<ComputerLoan {cloan.idLoan} of Computer {computer.idComputer} to User {user.idUser}>"
    assert cloan in user.computerLoansUser.all()
