import asyncio
from unittest.mock import AsyncMock, patch
from rest_framework.test import APIClient
from django.urls import reverse
from prices.models import Price  # Замените на путь к вашей модели
import pytest
from channels.testing import WebsocketCommunicator
from prices.consumer import CryptoTrackerConsumer  # Замените на путь к вашему консьюмеру
import json

@pytest.mark.django_db
def test_price_history_api():
    client = APIClient()

    Price.objects.create(ticket="ETHUSDT", price=3000.50)
    Price.objects.create(ticket="ETHUSDT", price=3001.75)

    response = client.get(reverse('price_history'), {'ticket': 'ETHUSDT'})
    
    assert response.status_code == 200, "API должен возвращать статус 200"

    data = response.json()
    assert len(data) == 2, "API должен вернуть 2 записи"
    assert data[0]['ticket'] == "ETHUSDT", "Тикет должен быть 'ETHUSDT'"
    assert float(data[0]['price']) == 3000.50, "Цена первой записи должна быть 3000.50"



@pytest.mark.asyncio
@pytest.mark.django_db
async def test_websocket_with_mock(mocker):
    # mock_data ={
    #     "s": "BTCUSDT",
    #     "p": "50000.00",
    #     "T": 1610000000000
    # }
    # mock_response = mocker.MagicMock()
    # mock_response.json.return_value = mock_data

    # # Patch 'requests.get' to return the mock response
    # mocker.patch("websockets.connect", return_value=mock_response)
    # # mock_ws = AsyncMock()
    # # mock_connect.return_value.__aenter__.return_value = mock_ws
    # # mock_ws.recv = AsyncMock(return_value=json.dumps())

    # communicator = WebsocketCommunicator(CryptoTrackerConsumer.as_asgi(), "/ws/prices/btcusdt")
    # connected = await communicator.connect()
    # assert connected, "WebSocket должен подключиться"
    # response = await communicator.receive_json_from()
    # assert "50000.00" in response, "Ответ должен содержать цену '50000.00'"

    # await communicator.disconnect()
        # Mock the websockets.connect function
    mock_connect = mocker.patch("websockets.connect")

    # Create an async mock for the WebSocket connection
    mock_ws = mocker.AsyncMock()
    # Configure the async context manager behavior
    mock_connect.return_value.__aenter__.return_value = mock_ws
    mock_connect.return_value.__aexit__.return_value = None

    # Mock the recv method to return specific data once
    mock_data = json.dumps({
        "s": "BTCUSDT",
        "p": "50000.00",
        "T": 1610000000000
    })
    mock_ws.recv.side_effect = [mock_data]  # Return once, then stop

    # Initialize the WebSocket communicator
    communicator = WebsocketCommunicator(CryptoTrackerConsumer.as_asgi(), "/ws/prices/btcusdt")
    
    # Connect to the WebSocket
    connected, _ = await communicator.connect()
    assert connected, "Failed to connect to WebSocket"

    # Give the check_price task time to run
    await asyncio.sleep(0.1)

    # Receive and verify the response
    response = await communicator.receive_from(timeout=1)
    print(f"Received response: {response}")
    assert "50000.00" in response, f"Expected price '50000.00' not found in response: {response}"

    # Disconnect
    await communicator.disconnect()
