from app.models.computers import Computer
from app import db


def test_index_computers(client, computer):
    response = client.get('/computers/')
    assert response.status_code == 200
    assert computer.brandComputer.encode('utf-8') in response.data
    assert computer.modelComputer.encode('utf-8') in response.data


def test_add_computer_page(client):
    response = client.get('/computers/add')
    assert response.status_code == 200


def test_add_computer(client):
    response = client.post('/computers/add', data={
        'brandComputer': 'HP',
        'modelComputer': 'Pavilion 15',
        'statusComputer': 'Active'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"HP" in response.data
    assert b"Pavilion 15" in response.data

    created = Computer.query.filter_by(brandComputer='HP', modelComputer='Pavilion 15').first()
    assert created is not None
    assert created.statusComputer == 'Active'


def test_update_computer_page(client, computer):
    response = client.get(f'/computers/update/{computer.idComputer}')
    assert response.status_code == 200
    assert computer.brandComputer.encode('utf-8') in response.data


def test_update_computer(client, computer):
    response = client.post(f'/computers/update/{computer.idComputer}', data={
        'brandComputer': 'Dell Updated',
        'modelComputer': 'Latitude 5430',
        'statusComputer': 'Maintenance'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Dell Updated" in response.data

    db.session.refresh(computer)
    assert computer.brandComputer == 'Dell Updated'
    assert computer.modelComputer == 'Latitude 5430'
    assert computer.statusComputer == 'Maintenance'


def test_delete_computer(client, computer):
    comp_id = computer.idComputer
    response = client.post(f'/computers/delete/{comp_id}', follow_redirects=True)
    assert response.status_code == 200

    deleted = db.session.get(Computer, comp_id)
    assert deleted is None
