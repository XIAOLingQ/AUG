from fastapi import FastAPI, Request
from pydantic import BaseModel
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

# 设置 GPU 编号
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
MODEL_PATH = "/root/autodl-tmp/train/"

# 检查设备
device = "cuda" if torch.cuda.is_available() else "cpu"

# 加载分词器
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)

# 加载模型，并启用 float16 加速
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
    trust_remote_code=True,
)

# 将模型移到 GPU 上
model = model.to(device).eval()

# 使用 torch.compile 进行编译加速（适用于 PyTorch 2.0 及以上版本）
try:
    model = torch.compile(model)
except Exception as e:
    print(f"模型编译失败: {e}，降级使用未编译模型")

# 定义对话历史数据结构
class Message(BaseModel):
    role: str
    content: str

# 定义请求体格式
class ConversationRequest(BaseModel):
    query: str
    history: list[Message] = []

# 初始化 FastAPI 应用
app = FastAPI()

@app.post("/generate")
async def generate_response(request_data: ConversationRequest):
    # 获取请求中的 query 和对话历史
    query = request_data.query
    history = request_data.history

    # 将当前用户输入加入对话历史
    history.append({"role": "user", "content": query})

    # 格式化对话为模型输入格式
    formatted_history = ""
    for turn in history:
        if turn["role"] == "user":
            formatted_history += f"用户: {turn['content']}\n"
        else:
            formatted_history += f"助手: {turn['content']}\n"

    # 定义最终输入
    inputs = tokenizer(formatted_history, return_tensors="pt", add_special_tokens=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # 定义生成参数
    gen_kwargs = {"max_length": 1000, "do_sample": True, "top_k": 5, "top_p": 0.95}

    # 启用推理模式
    with torch.inference_mode():
        # 执行推理
        outputs = model.generate(**inputs, **gen_kwargs)

    # 获取生成结果并解码
    outputs = outputs[:, inputs['input_ids'].shape[1]:]
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # 将助手的响应加入对话历史
    history.append({"role": "assistant", "content": result})

    # 返回生成结果和更新后的历史
    return {"response": result, "history": history}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
