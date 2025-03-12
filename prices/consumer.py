import asyncio
from collections import defaultdict
import datetime
import json
from statistics import mean

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import websockets

from prices.models import Price


class CryptoTrackerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ticket = self.scope["url_route"]["kwargs"]["price_pair"]
        self.ticket_group = "crypto_prices_" + self.ticket
        
        await self.channel_layer.group_add(self.ticket_group, self.channel_name)
        
        await self.accept()
        
        self.buffer = defaultdict(list)
        
        self.tracker_task = asyncio.create_task(self.check_price())
        self.save_data_task = asyncio.create_task(self.save_task())
        
        
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.ticket_group, self.channel_name)


    async def check_price(self):
        async with websockets.connect(f"wss://stream.binance.com:9443/ws/{self.ticket}@trade") as ws:
            while True:
                data = await ws.recv()
                data = json.loads(data)
                print(data)
                
                price = float(data['p'])

                self.buffer[data['s']].append(price)
                # Отправить обновление клиентам
                await self.channel_layer.group_send(
                    self.ticket_group,
                    {
                        'type': 'price_update',
                        'message': {'symbol': data['s'], 'price': str(price)}
                    }
                )
            
    
    async def save_task(self):
        while True:
            for symbol, prices in self.buffer.items():
                if prices:
                    try:
                        average_price = mean(prices)
                        await sync_to_async(Price.objects.create)(ticket=symbol, price=average_price)
                        self.buffer[symbol] = []  
                    except Exception as e:
                        print(f"Error saving {symbol}: {e}")
            await asyncio.sleep(10)
    
    async def price_update(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))
        