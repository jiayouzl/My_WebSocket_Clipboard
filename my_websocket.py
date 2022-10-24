# -*- coding: UTF-8 -*-

import datetime
from threading import Lock
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'f48761c63f406d6efc60838fb4dfeff1'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


def background_thread():
    """将服务器生成的事件发送给客户端的示例。"""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        now_time = datetime.datetime.now().strftime('%H:%M:%S')
        # socketio.emit('my_response', {'data': 'Server generated event ── ' + now_time, 'count': count})
        socketio.emit('my_response', {'data': 'Server event ── ' + now_time, 'count': count})


#http://192.168.5.181:5001
@app.route('/')
def index():
    return render_template('my_websocket.html', async_mode=socketio.async_mode)


@socketio.event
def my_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': message['data'], 'count': session['receive_count']})


@socketio.event
def my_broadcast_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': message['data'], 'count': session['receive_count']}, broadcast=True)


@socketio.event
def my_ping():
    emit('my_pong')


@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    # emit('my_response', {'data': 'Connected', 'count': 0})
    emit('my_response', {'data': '正在连接中.....', 'count': 0})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)