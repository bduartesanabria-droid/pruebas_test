def test_login_page_get(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"login" in response.data.lower() or b"iniciar" in response.data.lower() or b"usuario" in response.data.lower()


def test_login_success(client, user):
    response = client.post('/', data={
        'nameUser': user.nameUser,
        'passwordUser': user.passwordUser
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # The route redirects to user.index ('/User/')
    assert b"Usuarios" in response.data or b"Usuario" in response.data


def test_login_invalid_credentials(client):
    response = client.post('/', data={
        'nameUser': 'wronguser',
        'passwordUser': 'wrongpassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid credentials. Please try again." in response.data


def test_login_already_authenticated(client, user):
    with client.session_transaction() as session:
        session['_user_id'] = str(user.idUser)
        session['_fresh'] = True

    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert f"Welcome, {user.nameUser}!".encode('utf-8') in response.data


def test_dashboard_authenticated(authenticated_client, user):
    response = authenticated_client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert f"Welcome, {user.nameUser}!".encode('utf-8') in response.data


def test_dashboard_unauthenticated(client):
    response = client.get('/dashboard', follow_redirects=False)
    # Should redirect to login
    assert response.status_code == 302
    assert '/' in response.headers.get('Location', '')


def test_logout(authenticated_client):
    response = authenticated_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out." in response.data
