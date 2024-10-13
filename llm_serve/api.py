import os
import torch
import uvicorn
from fastapi import FastAPI, Request
from transformers import AutoModelForCausalLM, AutoTokenizer
from pydantic import BaseModel
from typing import List, Dict
from fastapi.responses import JSONResponse

# 设置环境变量
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

# 模型路径
MODEL_PATH = "/root/autodl-tmp/qwen/"

# 检查是否使用 GPU
device = "cuda" if torch.cuda.is_available() else "cpu"

# 初始化 tokenizer 和模型
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    device_map="cuda"
).eval()

# 创建 FastAPI 实例
app = FastAPI()

# 定义请求体结构
class ChatRequest(BaseModel):
    prompt: str
    history: List[Dict[str, str]]  # 历史记录，以 role 和 content 对象列表的形式

# API 路由处理 POST 请求
@app.post("/")
async def generate_response(request: ChatRequest):
    user_input = request.prompt
    history = request.history if request.history else []  # 如果没有历史，则初始化为空列表


    # 合并历史记录和当前输入
    conversation_history = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."}
    ]

    # 处理历史记录，使用 role 来保持一致性
    if history:
        for message in history:
            # 检查 message 中的 role 类型，直接追加到 conversation_history 中
            conversation_history.append({"role": message["role"], "content": message["content"]})

    # 添加当前用户的输入
    conversation_history.append({"role": "user", "content": user_input})

    # 打印调试信息，查看完整的对话历史
    print(f"Updated conversation history: {conversation_history}")

    # 使用千问模型的 chat 模板生成输入文本
    text = tokenizer.apply_chat_template(
        conversation_history,
        tokenize=False,
        add_generation_prompt=True
    )

    # 将生成的输入转换为模型可接受的格式
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    # 生成响应
    gen_kwargs = {"max_new_tokens": 5000, "do_sample": True, "top_k": 1}
    with torch.no_grad():
        generated_ids = model.generate(**model_inputs, **gen_kwargs)
        generated_ids = generated_ids[:, model_inputs.input_ids.shape[1]:]  # 截断输入部分

    # 解码生成的文本
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]


    history.append({"role": "assistant", "content": response})

    # 打印调试信息，查看最新的历史记录
    print(f"Updated history: {history}")

    # 返回生成的响应和历史
    return JSONResponse(content={
        "status": 200,
        "response": response,
        "history": history
    })

# 代码内启动 FastAPI 服务器
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6006)
