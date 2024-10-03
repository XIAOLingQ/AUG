import requests
from flask.json import jsonify
from plantuml import PlantUML
from zhipuai import ZhipuAI
from flask import Flask, Response, json, request
from dashscope import Generation
from dashscope.api_entities.dashscope_response import Role
from flask_cors import CORS

client = ZhipuAI(api_key="9e552efc10638d85e8042d40b9acbcce.jissfQ9lXpIbJRfK")  # 请填写您自己的APIKey

app = Flask(__name__)
CORS(app, resources="/*")

plantuml = PlantUML(url='http://27.25.158.240:50950/plantuml/png/')
messages = []  # Store all messages


def generate_chat_completion(messages):
    return client.chat.completions.create(
        model="glm-4",
        messages=messages,
    )


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


@app.route('/llm/request')
def stream_numbers():
    global messages
    print(messages)
    query = request.args.get('query', default='default query')

    def chat():
        print(query)
        messages.append({'role': Role.USER, 'content': query})
        whole_message = ''
        responses = generate_chat_completion(messages)
        responses = responses.choices[0].message.content

        part_message = responses
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


@app.route('/reset_messages', methods=['POST'])
def reset_messages():
    global messages
    messages = []  # Clear the messages list
    return jsonify({"message": "Messages reset successfully."}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
