import io
import json
import qrcode
from PIL import Image
from app.models.users import User
from app import db


def test_index_users(client, user):
    response = client.get('/User/')
    assert response.status_code == 200
    assert b"Usuarios" in response.data or user.nameUser.encode('utf-8') in response.data


def test_add_user_page(client):
    response = client.get('/User/add')
    assert response.status_code == 200


def test_add_user(client):
    response = client.post('/User/add', data={
        'nameUser': 'carlos_new',
        'passwordUser': 'secret456'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"carlos_new" in response.data

    created_user = User.query.filter_by(nameUser='carlos_new').first()
    assert created_user is not None
    assert created_user.passwordUser == 'secret456'


def test_edit_user_page(client, user):
    response = client.get(f'/User/edit/{user.idUser}')
    assert response.status_code == 200
    assert user.nameUser.encode('utf-8') in response.data


def test_edit_user(client, user):
    response = client.post(f'/User/edit/{user.idUser}', data={
        'nameUser': 'updated_user_name',
        'passwordUser': 'updated_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"updated_user_name" in response.data

    db.session.refresh(user)
    assert user.nameUser == 'updated_user_name'
    assert user.passwordUser == 'updated_password'


def test_detail_user(client, user):
    response = client.get(f'/User/detail/{user.idUser}')
    assert response.status_code == 200
    assert user.nameUser.encode('utf-8') in response.data


def test_delete_user(client, user):
    user_id = user.idUser
    response = client.get(f'/User/delete/{user_id}', follow_redirects=True)
    assert response.status_code == 200

    deleted_user = db.session.get(User, user_id)
    assert deleted_user is None


def test_generate_qr_endpoint(client, user):
    response = client.get(f'/User/qr/{user.idUser}')
    assert response.status_code == 200
    assert response.mimetype == 'image/png'
    assert response.data.startswith(b'\x89PNG\r\n\x1a\n')


def test_read_qr_no_file(client):
    response = client.post('/User/read_qr')
    assert response.status_code == 400
    assert "No se ha proporcionado una imagen de QR" in response.data.decode('utf-8')


def test_read_qr_invalid_image_no_qr(client):
    # Blank image without QR
    img = Image.new('RGB', (100, 100), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    data = {
        'qr_image': (img_bytes, 'blank.png')
    }
    response = client.post('/User/read_qr', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert "No se pudo leer el código QR" in response.data.decode('utf-8')


def test_read_qr_success(client, user):
    qr_data = json.dumps({'ID': user.idUser, 'Name': user.nameUser})
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    response = client.post('/User/read_qr', data={
        'qr_image': (img_bytes, 'user_qr.png')
    }, content_type='multipart/form-data')

    assert response.status_code == 200
    assert user.nameUser.encode('utf-8') in response.data


def test_read_qr_user_not_found(client):
    qr_data = json.dumps({'ID': 99999, 'Name': 'non_existent'})
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    response = client.post('/User/read_qr', data={
        'qr_image': (img_bytes, 'user_qr.png')
    }, content_type='multipart/form-data')

    assert response.status_code == 404
    assert "Usuario no encontrado" in response.data.decode('utf-8')


def test_read_qr_invalid_payload_without_id(client):
    qr_data = json.dumps({'Name': 'NoIDUser'})
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    response = client.post('/User/read_qr', data={
        'qr_image': (img_bytes, 'user_qr.png')
    }, content_type='multipart/form-data')

    assert response.status_code == 400
    assert "El código QR no contiene un ID de usuario válido" in response.data.decode('utf-8')
