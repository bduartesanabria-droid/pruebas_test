from app.models.rooms import Room
from app import db


def test_index_rooms(client, room):
    response = client.get('/room/')
    assert response.status_code == 200
    assert room.name.encode('utf-8') in response.data


def test_add_room_page(client):
    response = client.get('/room/add')
    assert response.status_code == 200


def test_add_room(client):
    response = client.post('/room/add', data={
        'name': 'Sala Multimedial C',
        'description': 'Sala equipada con proyectores y audio'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Sala Multimedial C" in response.data

    created = Room.query.filter_by(name='Sala Multimedial C').first()
    assert created is not None
    assert created.description == 'Sala equipada con proyectores y audio'


def test_edit_room_page(client, room):
    response = client.get(f'/room/edit/{room.id}')
    assert response.status_code == 200
    assert room.name.encode('utf-8') in response.data


def test_edit_room(client, room):
    response = client.post(f'/room/edit/{room.id}', data={
        'name': 'Sala de Lectura A - Renovada',
        'description': 'Espacio renovado con iluminacion natural'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Sala de Lectura A - Renovada" in response.data

    db.session.refresh(room)
    assert room.name == 'Sala de Lectura A - Renovada'
    assert room.description == 'Espacio renovado con iluminacion natural'


def test_delete_room(client, room):
    room_id = room.id
    response = client.get(f'/room/delete/{room_id}', follow_redirects=True)
    assert response.status_code == 200

    deleted = db.session.get(Room, room_id)
    assert deleted is None
