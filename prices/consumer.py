import asyncio
from collections import defaultdict
import json
from statistics import mean
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import websockets

from prices.models import Price

class CheckPriceSingleton:
    instances = {}
    send_tasks = {}
    buffers = {} 
    channel_layer = None

    def __new__(cls, ticker: str):
        if ticker not in cls.instances:
            instance = super(CheckPriceSingleton, cls).__new__(cls)
            cls.instances[ticker] = instance
            cls.buffers[ticker] = defaultdict(list) 
        return cls.instances[ticker]

    def __init__(self, ticker: str):
        if not hasattr(self, '_initialized'):
            self.ticker = ticker
            self._initialized = True

    async def check_price(self, group_name: str):
        async with websockets.connect(f"wss://stream.binance.com:9443/ws/{self.ticker}@trade") as ws:
            while True:
                data = await ws.recv()
                data = json.loads(data)
                # print(f"{self.ticker} received: {data}")
                
                price = float(data['p'])
                self.buffers[self.ticker][data['s']].append(price)
                await self.channel_layer.group_send(
                    group_name,
                    {
                        'type': 'price_update',
                        'message': data
                    }
                )

    def create_task_sender(self, func, group_name: str):
        if self.ticker not in self.send_tasks:
            self.send_tasks[self.ticker] = asyncio.create_task(func(group_name))

class CryptoTrackerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ticket = self.scope["url_route"]["kwargs"]["price_pair"].lower()
        self.ticket_group = "crypto_prices_" + self.ticket
        
        await self.channel_layer.group_add(self.ticket_group, self.channel_name)
        await self.accept()
        
        self.singleton = CheckPriceSingleton(self.ticket)
        self.singleton.channel_layer = self.channel_layer  # Pass channel_layer to singleton
        self.singleton.create_task_sender(self.singleton.check_price, self.ticket_group)
        
        self.save_data_task = asyncio.create_task(self.save_task())
        
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.ticket_group, self.channel_name)

    async def save_task(self):
        while True:
            buffer = self.singleton.buffers[self.ticket]
            for symbol, prices in buffer.items():
                if prices:
                    try:
                        average_price = mean(prices)
                        await sync_to_async(Price.objects.create)(ticket=symbol, price=average_price)
                        buffer[symbol] = []
                        # print(f"Saved {symbol}: {average_price}")
                    except Exception as e:
                        print(f"Error saving {symbol}: {e}")
            await asyncio.sleep(10)
    
    async def price_update(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))