import requests
from dashscope.api_entities.dashscope_response import Role
from flask import Flask, jsonify, Response, json, request
from flask_cors import CORS
from plantuml import PlantUML

# 初始化Flask应用
app = Flask(__name__)
CORS(app, resources="/*")  # 允许跨域

# 存储所有会话消息
messages = []
plantuml = PlantUML(url='http://27.25.158.240:50950/plantuml/png/')
# 大模型后端 URL
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

# 调用大模型的生成接口
def call_large_model_backend(messages, query):
    # 构造请求体
    payload = {
        "prompt": query,    # 使用 "prompt" 来匹配 FastAPI 接口定义
        "history": messages # 包含上下文的消息历史
    }

    # 设置请求头
    headers = {
        'Content-Type': 'application/json'  # 保持 JSON 格式
    }

    # 发送请求到模型后端
    response = requests.post(model_backend_url, headers=headers, data=json.dumps(payload))

    # 检查请求是否成功
    if response.status_code == 200:
        # 返回结果，假设返回 JSON 格式
        return response.json()  # 返回的是 JSON 对象，包含 "response" 和 "history"
    else:
        # 错误处理
        print(f"请求失败，状态码: {response.status_code}")
        return None


# 流式返回模型响应
@app.route('/llm/request', methods=['GET'])
def chat_with_llm():
    global messages
    query = request.args.get('query', default='default query')

    # 新消息加入上下文
    messages.append({"role": "user", "content": query})

    # 调用大模型后端
    response = call_large_model_backend(messages, query)

    if response.get('status') == 200:
        response_json = response  # 解析大模型返回的JSON
        model_reply = response_json.get('response', '')  # 从模型返回的结果中获取回复
        print(model_reply)
        messages.append({"role": "assistant", "content": model_reply})

        def chat():
            print(query)
            messages.append({'role': Role.USER, 'content': query})
            whole_message = model_reply

            part_message = model_reply
            whole_message += part_message
            print(part_message, end='')
            json_data = json.dumps({"message": part_message})
            yield f"data: {json_data}\n\n"

            messages.append({'role': 'assistant', 'content': whole_message})
            json_data = json.dumps({"message": 'done'})
            yield f"data: {json_data}\n\n"
            print('结束')

        headers = {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
        return Response(chat(), content_type='text/event-stream', headers=headers)
    else:
        return jsonify({"error": f"Failed to call model backend. Status code: {response.get('status')}"}, 500)

# 重置消息记录
@app.route('/reset_messages', methods=['POST'])
def reset_messages():
    global messages
    messages = []  # 清空消息记录
    return jsonify({"message": "Messages reset successfully."}), 200

# 启动Flask应用
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
