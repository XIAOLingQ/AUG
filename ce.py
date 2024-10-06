import os
import torch
import uvicorn
from fastapi import FastAPI, Request
from transformers import AutoModelForCausalLM, AutoTokenizer
from pydantic import BaseModel
from typing import List, Dict
from fastapi.responses import JSONResponse

os.environ['CUDA_VISIBLE_DEVICES'] = '0'
MODEL_PATH = "/root/autodl-tmp/train/"

device = "cuda" if torch.cuda.is_available() else "cpu"

# 初始化 tokenizer 和模型
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    trust_remote_code=True,
    device_map="auto"
).eval()

# 创建 FastAPI 实例
app = FastAPI()


# 定义请求体结构
class ChatRequest(BaseModel):
    prompt: str
    history: List[Dict[str, str]]  # 历史记录，以 user: message 对象列表的形式


# 模拟用户历史记录存储 (可以改为数据库)
user_history = {}


# API 路由处理 POST 请求
@app.post("/")
async def generate_response(request: ChatRequest):
    user_input = request.prompt
    history = request.history
    print(history)

    # 合并历史记录和当前输入，使用 .get() 方法避免 KeyError
    conversation_history = history

    # 生成输入
    inputs = tokenizer.apply_chat_template(conversation_history,
                                           add_generation_prompt=True,
                                           tokenize=True,
                                           return_tensors="pt",
                                           return_dict=True)
    inputs = inputs.to(device)

    # 生成响应
    gen_kwargs = {"max_length": 2500, "do_sample": True, "top_k": 1}
    with torch.no_grad():
        outputs = model.generate(**inputs, **gen_kwargs)
        outputs = outputs[:, inputs['input_ids'].shape[1]:]
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # 保存新的用户历史记录
    history.append({"user": user_input, "assistant": response})
    print(history)
    # 返回生成的响应和历史
    return JSONResponse(content={
        "status": 200,
        "response": response,
        "history": history
    })


# 代码内启动 FastAPI 服务器
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6006)

