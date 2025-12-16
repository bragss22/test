import uuid

import pytest


@pytest.mark.asyncio
async def test_register_token_and_order_flow(async_client, db_session):
    """Полный сценарий: регистрация, получение токена, создание заказа."""
    # Регистрация
    unique_id = uuid.uuid4().hex[:8]
    test_email = f'test_{unique_id}@example.com'

    # Регистрация
    register_data = {
        'email': test_email,
        'password': 'password123'
    }

    response = await async_client.post('/register', json=register_data)
    print(response.text)
    assert response.status_code == 201

    # Получение токена
    login_data = {
        'username': test_email,
        'password': 'password123'
    }

    response = await async_client.post(
        '/token',
        data=login_data
    )
    assert response.status_code == 200

    token_data = response.json()
    token = token_data.get('access_token')
    assert token is not None

    headers = {'Authorization': f'Bearer {token}'}

    # Создание заказа
    order_payload = {
        'items': [{'sku': 'TEST-ITEM-001', 'qty': 2}],
        'total_price': 19.98
    }

    response = await async_client.post(
        '/orders',
        json=order_payload,
        headers=headers
    )
    assert response.status_code == 201

    order_data = response.json()
    order_id = order_data['id']

    # Получение заказа
    response = await async_client.get(f'/orders/{order_id}')
    assert response.status_code == 200

    order_response = response.json()
    assert order_response['id'] == order_id
    assert order_response['items'] == order_payload['items']
    assert float(order_response['total_price']) == order_payload['total_price']
