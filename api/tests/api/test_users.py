import pytest


@pytest.fixture
def user_base_url():
    return '/users'


@pytest.mark.parametrize('user_exists', [True, False])
def test_create_user(client, user_base_url, test_user, user_exists,
                     mock_user_save,
                     mock_get_user_by_username,
                     mock_user_status_rel):
    response = client.post(user_base_url, json=test_user)
    if user_exists:
        assert response.status_code == 409
    else:
        assert response.status_code == 201
        json = response.json()
        assert json['_id']
        assert json['username'] == 'test'
        assert json['isAdmin'] == False

# Very easy to add more tests here, especially since everything is already mocked
