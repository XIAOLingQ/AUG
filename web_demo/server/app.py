import time
import requests
import schedule
from flask import Flask, jsonify, request, json, Response
from flask_cors import CORS
from plantuml import PlantUML
from datetime import datetime, timedelta
import threading

# 初始化Flask应用
app = Flask(__name__)
CORS(app, resources="/*")  # 允许跨域

# 存储用户的会话消息（以 user_id 为键），并记录每个用户的最后活动时间
user_messages = {}
user_last_active = {}
plantuml = PlantUML(url='http://27.25.158.240:50950/plantuml/png/')
model_backend_url = "http://27.25.158.240:43787"


@app.route('/get_uml', methods=['POST'])
def get_uml():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "No JSON received"}), 400
    markdown_content = data['markdown']
    uml_code = markdown_content
    try:
        url_uml = plantuml.get_url(uml_code)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"url": url_uml})


# 模型后端调用接口
def call_large_model_backend(messages, query):
    payload = {
        "prompt": query,
        "history": messages
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(model_backend_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return response.json()
    else:
        print(f"请求失败，状态码: {response.status_code}")
        return None


# 流式返回模型响应
@app.route('/llm/request', methods=['GET'])
def chat_with_llm():
    query = request.args.get('query', default='default query')
    user_id = request.args.get('user_id', default='guest')

    if user_id not in user_messages:
        user_messages[user_id] = []

    # 记录用户的最后活动时间
    user_last_active[user_id] = datetime.now()

    user_messages[user_id].append({"role": "user", "content": query})

    print(user_messages)

    response = call_large_model_backend(user_messages[user_id], query)

    if response.get('status') == 200:
        model_reply = response.get('response', '')

        user_messages[user_id].append({"role": "assistant", "content": model_reply})

        def chat():
            part_message = model_reply
            yield f"data: {json.dumps({'message': part_message})}\n\n"
            user_messages[user_id].append({'role': 'assistant', 'content': part_message})
            yield f"data: {json.dumps({'message': 'done'})}\n\n"

        headers = {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
        return Response(chat(), content_type='text/event-stream', headers=headers)
    else:
        return jsonify({"error": "Failed to call model backend."}), 500


# 重置特定用户的消息记录
@app.route('/reset_messages', methods=['POST'])
def reset_messages():
    user_id = request.json.get('user_id')
    if user_id and user_id in user_messages:
        user_messages[user_id] = []  # 清空特定用户的消息记录
        return jsonify({"message": f"Messages for user {user_id} reset successfully."}), 200
    else:
        return jsonify({"error": "User ID not provided or not found."}), 400


# 定期清理超过10分钟无活动的用户消息记录
def clear_inactive_users():
    global user_messages, user_last_active
    now = datetime.now()
    inactive_users = []

    for user_id, last_active in user_last_active.items():
        if now - last_active > timedelta(minutes=10):
            inactive_users.append(user_id)

    for user_id in inactive_users:
        del user_messages[user_id]
        del user_last_active[user_id]
        print(f"用户 {user_id} 的消息记录已删除，由于10分钟无活动")


# 使用 schedule 每天定时清理所有用户消息记录
def clear_all_messages():
    global user_messages
    user_messages = {}  # 清空所有用户的消息记录
    print("所有用户的消息记录已清除")


# 使用 schedule 定时任务
schedule.every().day.at("00:00").do(clear_all_messages)

# 每分钟检查一次是否有无活动超过10分钟的用户
schedule.every(1).minutes.do(clear_inactive_users)


# 启动Flask应用
if __name__ == '__main__':
    # 在 Flask 主线程中启动定期任务
    def run_scheduler():
        while True:
            schedule.run_pending()  # 运行所有已安排的任务
            time.sleep(1)

    # 启动定时任务调度器
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

    # 启动Flask服务器
    app.run(debug=True, host='0.0.0.0', port=5000)
