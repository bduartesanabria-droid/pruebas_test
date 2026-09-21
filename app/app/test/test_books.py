from app.models.books import Book
from app.models.authors import Author
from app import db


def test_index_books(client, book):
    response = client.get('/Book/')
    assert response.status_code == 200
    assert book.titleBook.encode('utf-8') in response.data


def test_add_book_page(client, author):
    response = client.get('/Book/add')
    assert response.status_code == 200
    assert author.nameAuthor.encode('utf-8') in response.data


def test_add_book(client, author):
    response = client.post('/Book/add', data={
        'titleBook': 'El Coronel no tiene quien le escriba',
        'authorId': author.idAuthor
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"El Coronel no tiene quien le escriba" in response.data

    created = Book.query.filter_by(titleBook='El Coronel no tiene quien le escriba').first()
    assert created is not None
    assert created.authorId == author.idAuthor


def test_edit_book_page(client, book, author):
    response = client.get(f'/Book/edit/{book.idBook}')
    assert response.status_code == 200
    assert book.titleBook.encode('utf-8') in response.data
    assert author.nameAuthor.encode('utf-8') in response.data


def test_edit_book(client, book, author):
    # Create another author to change relationship
    author2 = Author(nameAuthor="Mario Vargas Llosa", nationalityAuthor="Peruvian")
    db.session.add(author2)
    db.session.commit()

    response = client.post(f'/Book/edit/{book.idBook}', data={
        'titleBook': 'Cien Anos de Soledad - Edicion Especial',
        'authorId': author2.idAuthor
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Cien Anos de Soledad - Edicion Especial" in response.data

    db.session.refresh(book)
    assert book.titleBook == 'Cien Anos de Soledad - Edicion Especial'
    assert book.authorId == author2.idAuthor


def test_delete_book(client, book):
    book_id = book.idBook
    response = client.get(f'/Book/delete/{book_id}', follow_redirects=True)
    assert response.status_code == 200

    deleted = db.session.get(Book, book_id)
    assert deleted is None
