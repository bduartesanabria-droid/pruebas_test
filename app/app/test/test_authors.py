from app.models.authors import Author
from app.models.books import Book
from app import db


def test_index_authors(client, author):
    response = client.get('/Author/')
    assert response.status_code == 200
    assert author.nameAuthor.encode('utf-8') in response.data


def test_list_author_books(client, author, book):
    response = client.get(f'/Author/list/{author.idAuthor}')
    assert response.status_code == 200
    assert book.titleBook.encode('utf-8') in response.data


def test_add_author_page(client):
    response = client.get('/Author/add')
    assert response.status_code == 200


def test_add_author(client):
    response = client.post('/Author/add', data={
        'nameAuthor': 'Isabel Allende',
        'nationalityAuthor': 'Chilean'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Isabel Allende" in response.data

    created = Author.query.filter_by(nameAuthor='Isabel Allende').first()
    assert created is not None
    assert created.nationalityAuthor == 'Chilean'


def test_edit_author_page(client, author):
    response = client.get(f'/Author/edit/{author.idAuthor}')
    assert response.status_code == 200
    assert author.nameAuthor.encode('utf-8') in response.data


def test_edit_author(client, author):
    response = client.post(f'/Author/edit/{author.idAuthor}', data={
        'nameAuthor': 'Gabriel G. Marquez',
        'nationalityAuthor': 'Colombian'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Gabriel G. Marquez" in response.data

    db.session.refresh(author)
    assert author.nameAuthor == 'Gabriel G. Marquez'


def test_delete_author(client, author):
    author_id = author.idAuthor
    response = client.get(f'/Author/delete/{author_id}', follow_redirects=True)
    assert response.status_code == 200

    deleted = db.session.get(Author, author_id)
    assert deleted is None
