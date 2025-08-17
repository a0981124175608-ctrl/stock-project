# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 17:17:08 2025

@author: user
"""

# realtime_mock.py
import time, random, threading
from flask_socketio import join_room, leave_room
from extensions import socketio

_stream_threads = {}

@socketio.on('join')
def on_join(data):
    stock = (data or {}).get('stock_code')
    if not stock:
        return
    join_room(stock)
    if stock not in _stream_threads:
        _stream_threads[stock] = _start_mock_stream(stock)

@socketio.on('leave')
def on_leave(data):
    stock = (data or {}).get('stock_code')
    if stock:
        leave_room(stock)

def _start_mock_stream(stock):
    def run():
        price = 100.0
        while True:
            bids = [{"price": round(price - i*0.1, 2), "volume": random.randint(10, 200)} for i in range(5)]
            asks = [{"price": round(price + i*0.1, 2), "volume": random.randint(10, 200)} for i in range(5)]
            socketio.emit(
                'order_book_update',
                {"stock_code": stock, "data": {"bids": bids, "asks": asks, "ts": int(time.time()*1000)}},
                room=stock
            )

            price += random.uniform(-0.25, 0.25)
            tick = {
                "ts": int(time.time()*1000),
                "price": round(price, 2),
                "volume": random.randint(1, 80),
                "side": 'buy' if random.random() > 0.5 else 'sell'
            }
            socketio.emit('tick_update', {"stock_code": stock, "data": tick}, room=stock)

            time.sleep(1)
    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t