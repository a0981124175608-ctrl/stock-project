# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 23:24:55 2025

@author: user
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.message import Message
from models.favorite import Favorite
from extensions import db,socketio
from pytz import timezone
import yfinance as yf
import time, random, threading ,requests
from flask_socketio import join_room, leave_room
import os 

stock_bp = Blueprint('stock', __name__, url_prefix='/stock')

# 股票詳細頁
@stock_bp.route('/detail/<stock_code>')
@login_required
def stock_detail(stock_code):
    messages = Message.query.filter_by(stock_code=stock_code).order_by(Message.timestamp.asc()).all()

    taiwan = timezone('Asia/Taipei')
    for msg in messages:
        msg.local_time = msg.timestamp.astimezone(taiwan).strftime('%Y-%m-%d %H:%M:%S')

    # 取得使用者收藏
    user_favorites = [fav.stock_code for fav in current_user.favorites]

    return render_template('stock_detail.html',
                           stock_code=stock_code,
                           messages=messages,
                           user_favorites=user_favorites)

# 收藏/取消收藏
@stock_bp.route('/toggle_favorite', methods=['POST'])
@login_required
def toggle_favorite():
    stock_code = request.json.get('stock_code')
    if not stock_code:
        return jsonify({'status': 'error', 'message': '缺少股票代碼'}), 400

    fav = Favorite.query.filter_by(user_id=current_user.id, stock_code=stock_code).first()

    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({'status': 'removed'})
    else:
        new_fav = Favorite(user_id=current_user.id, stock_code=stock_code)
        db.session.add(new_fav)
        db.session.commit()
        return jsonify({'status': 'added'})
    
@stock_bp.route('/my_favorites')
@login_required
def my_favorites():
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    return render_template('my_favorites.html', favorites=favorites)
    
# 即時股票搜尋（yfinance）
@stock_bp.route('/search', methods=['GET'])
@login_required
def search_stock():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({"stocks": []})

    try:
        ticker = yf.Ticker(f"{query}.TW")  # 台股代碼要加 .TW
        info = ticker.info
        result = {
            "code": query,
            "name": info.get("shortName", ""),
            "price": info.get("regularMarketPrice", 0),
            "change": info.get("regularMarketChange", 0),
            "volume": info.get("regularMarketVolume", 0)
        }
        return jsonify({"stocks": [result]})
    except Exception as e:
        return jsonify({"stocks": [], "error": str(e)})
    
@stock_bp.route('/kline/<stock_code>')
@login_required
def get_kline(stock_code):
    try:
        ticker = yf.Ticker(f"{stock_code}.TW")
        info = ticker.info
        name = info.get("longName", info.get("shortName", stock_code))

        df = ticker.history(period="180d", interval="1d")

        data = []
        for date, row in df.iterrows():   # ⭐ 注意縮排
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": row["Volume"]
            })

        return jsonify({
            "name": name,
            "kline": data
        })
    except Exception as e:
        return jsonify({"error": str(e)})
    
@stock_bp.route('/stock_name/<stock_code>')
@login_required
def get_stock_name(stock_code):
    try:
        ticker = yf.Ticker(f"{stock_code}.TW")
        info = ticker.info
        name = info.get("longName", info.get("shortName", stock_code))
        return jsonify({"code": stock_code, "name": name})
    except Exception as e:
        return jsonify({"error": str(e)})
   
_stream_threads = {}

def _parse_side(price_str, vol_str):
    """把 TWSE MIS 以底線分隔的價/量字串轉成 [{'price':..,'volume':..}, ...]"""
    ps = [x for x in (price_str or "").split("_") if x and x != "-"]
    vs = [x for x in (vol_str or "").split("_") if x and x != "-"]
    out = []
    for p, v in zip(ps, vs):
        try:
            out.append({"price": float(p), "volume": int(float(v))})
        except Exception:
            pass
    return out[:5]

def _start_twse_stream(room: str):
    """
    從 TWSE MIS 拉真實五檔/最新價，每秒推一次到該股票的 room。
    room/stock 一律用字串（例如 "2330"）。
    """
    stock = str(room)
    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
    # 同時查上市/上櫃，哪個有資料就回哪個
    ex_ch = f"tse_{stock}.tw|otc_{stock}.tw"
    headers = {
        "Referer": f"https://mis.twse.com.tw/stock/fibest.jsp?ex_ch=tse_{stock}.tw",
        "User-Agent": "Mozilla/5.0",
    }

    def run():
        while True:
            try:
                params = {"ex_ch": ex_ch, "json": "1", "delay": "0", "_": int(time.time() * 1000)}
                r = requests.get(url, params=params, headers=headers, timeout=3)
                j = r.json()
                arr = j.get("msgArray") or []
                if not arr:
                    print(f"[TWSE] empty for {stock}: {j.get('rtmessage') or 'no msgArray'}")
                    time.sleep(1)
                    continue

                rec = arr[0]
                bids = _parse_side(rec.get("b"), rec.get("g"))  # 買價、買量
                asks = _parse_side(rec.get("a"), rec.get("f"))  # 賣價、賣量
                ts = int(time.time() * 1000)

                # 五檔 → 指定房間；同時全域廣播一份方便你除錯（確認前端有收得到）
                payload_book = {"stock_code": stock, "data": {"bids": bids, "asks": asks, "ts": ts}}
                print(f"[EMIT] BOOK to room={stock} bids={len(bids)} asks={len(asks)}")
                socketio.emit("order_book_update", payload_book, room=stock)
                socketio.emit("order_book_update", payload_book)  # ← 驗證用，之後可刪

                # 逐筆（MIS 沒真正 tick 串流，這裡用最近成交價/量拼一筆）
                last = rec.get("z")
                tv = rec.get("tv")
                try:
                    last_val = float(last) if last and last != "-" else None
                    tv_val = int(float(tv)) if tv and tv != "-" else None
                except Exception:
                    last_val = tv_val = None

                if last_val is not None and tv_val is not None:
                    payload_tick = {"stock_code": stock,
                                    "data": {"ts": ts, "price": last_val, "volume": tv_val, "side": "buy"}}
                    print(f"[EMIT] TICK to room={stock} price={last_val} vol={tv_val}")   # ★新增
                    socketio.emit("order_book_update", payload_book)  # ★驗證用全域廣播
                    socketio.emit("tick_update", payload_tick)    

                print(f"[TWSE] {stock} bids:{len(bids)} asks:{len(asks)} last:{last} tv:{tv}")
            except Exception as e:
                print(f"[TWSE] error for {stock}: {e}")
            time.sleep(1)

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t

@socketio.on('connect')
def _on_connect():
    print(f"[WS] connect pid={os.getpid()}")

@socketio.on('join')
def _on_join(data):
    room = str((data or {}).get('stock_code') or '')
    print(f"[JOIN] pid={os.getpid()} room={room!r}")
    if not room:
        return
    join_room(room)
    # ✅ 沒有線程才啟動，避免重複開
    if room not in _stream_threads:
        _stream_threads[room] = _start_twse_stream(room)
        print(f"[STREAM] started for {room}")

@socketio.on('disconnect')
def _on_disconnect():
    print(f"[WS] disconnect pid={os.getpid()}")
#測試用
@stock_bp.route('/whoami') 
def whoami():
    import os
    return f"pid={os.getpid()}"

# 手動觸發一筆（驗證前端一定收得到；正式用不一定需要）
@stock_bp.route('/_emit_test')
def _emit_test():
    from flask import request
    code = str(request.args.get('code', '2330'))
    ts = int(time.time() * 1000)
    bids = [{"price": 100 - i*0.1, "volume": 50 + i*5} for i in range(5)]
    asks = [{"price": 100 + i*0.1, "volume": 50 + i*5} for i in range(5)]
    payload_book = {"stock_code": code, "data": {"bids": bids, "asks": asks, "ts": ts}}
    payload_tick = {"stock_code": code, "data": {"ts": ts, "price": 100.0, "volume": 10, "side": "buy"}}
    socketio.emit('order_book_update', payload_book, room=code)
    socketio.emit('tick_update', payload_tick, room=code)
    return "ok"