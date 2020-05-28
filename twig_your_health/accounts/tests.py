from django.test import TestCase

def test_login():
    self_url = "{}/{}/auth/self".format(prefix, version)
    login_url = "{}/{}/auth/login".format(prefix, version)
    # prohibited with wrong token
    headers = {
        "Authorization": "Bearer s"
    }
    response = client.get(self_url, headers=headers)
    assert response.status_code == 403
    response = client.post(login_url,
                           json={'user': {'email': user.email}})
    assert response.status_code == 200
    data = response.json()
    assert data['user']['id'] == user.id
    assert data['user']['email'] == user.email
    assert data['user']['type'] == user.type
