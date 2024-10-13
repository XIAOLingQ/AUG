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
MODEL_PATH = "/root/autodl-tmp/AUG/"

# 检查是否使用 GPU
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
gen_kwargs = {"max_length": 2500, "do_sample": True, "top_k": 1}
# 定义请求体结构
class ChatRequest(BaseModel):
    prompt: str
    history: List[Dict[str, str]]  # 历史记录，以 role 和 content 对象列表的形式

# API 路由处理 POST 请求
@app.post("/")
async def generate_response(request: ChatRequest):
    user_input = request.prompt
    history = request.history if request.history else []  # 如果没有历史，则初始化为空列表

    # 打印调试信息，查看历史记录
    print(f"Received history: {history}")

    # 合并历史记录和当前输入
    conversation_history = [
        {"role": "system", "content": "你是AUG需求助手，你的任务是协助开发者进行需求建模。"}
    ]

    # 处理历史记录，使用 role 来保持一致性
    if history:
        for message in history:
            # 检查 message 中的 role 类型，直接追加到 conversation_history 中
            conversation_history.append({"role": message["role"], "content": message["content"]})

    inputs = tokenizer.apply_chat_template(conversation_history,
                                           add_generation_prompt=True,
                                           tokenize=True,
                                           return_tensors="pt",
                                           return_dict=True
                                           )

    # 生成响应
    gen_kwargs = {"max_new_tokens": 5000, "do_sample": True, "top_k": 1}



    with torch.no_grad():
        outputs = model.generate(**inputs, **gen_kwargs)
        outputs = outputs[:, inputs['input_ids'].shape[1]:]

    # 解码生成的文本
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)


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
