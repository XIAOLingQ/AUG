import asyncio
import streamlit as st
import uuid
import re
import httpx
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stream.components.uml_editor import render_uml_editor

# Constants
DEFAULT_USER_ID = str(uuid.uuid4())
llm_serve_url = "http://36.50.226.35:33642"

if 'messages' not in st.session_state:
    st.session_state.messages = []

# 添加一个新的状态来追踪是否需要重置
if 'should_reset' not in st.session_state:
    st.session_state.should_reset = False

# Page config
st.set_page_config(page_title="Chat Application", layout="wide")

def reset_chat():
    """Reset chat history"""
    st.session_state.should_reset = True

def create_message_container(role, content, message_idx):
    with st.chat_message(role):
        parts = re.split(r'(```[\s\S]*?```)', content, flags=re.DOTALL)
        
        for i, part in enumerate(parts):
            stripped_part = part.strip()
            if stripped_part.startswith('```') and stripped_part.endswith('```'):
                unique_key = f"{role}_{message_idx}_{i}"
                code_key = f"code_{unique_key}"
                
                code = stripped_part.strip('`').strip()
                first_line = code.split('\n')[0] if '\n' in code else ''
                
                if first_line.lower() in ['plantuml', 'uml']:
                    code = '\n'.join(code.split('\n')[1:])
                    if code_key not in st.session_state:
                        st.session_state[code_key] = code
                    
                    if '@startuml' in code.lower() and '@enduml' in code.lower():
                        # 只显示编辑器，不显示图像
                        render_uml_editor(code_key, message_idx)
            else:
                if stripped_part:
                    st.markdown(stripped_part)

async def get_bot_response(messages_history):
    timeout = httpx.Timeout(30.0, connect=60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(
                llm_serve_url,
                json={'messages': messages_history},
                timeout=timeout
            )
            
            response_data = response.json()
            print(f"原始响应: {response_data}")
            
            if isinstance(response_data, dict) and response_data.get('status') == 200:
                content = response_data.get('data', {}).get('content', '')
                if content:
                    return content
            return "无法获取有效响应"
                        
        except Exception as e:
            print(f"API请求错: {str(e)}")
            return f"发生错误: {str(e)}"

def main():
    # 检查是否需要重置
    if st.session_state.should_reset:
        st.session_state.messages = []
        st.session_state.should_reset = False
    
    # 添加样式
    st.markdown("""
        <style>
        /* ===== 聊天输入框样式 ===== */
        /* 输入框容器：固定在底部，自适应主题背景色 */
        div[data-testid="stChatInput"] {
            position: fixed !important;          /* 固定定位 */
            bottom: 16px !important;               /* 贴底部 */
            left: 20px !important;              /* 左侧留白 */
            padding: 0 !important;              /* 移除内边距使容器与输入框大小一致 */
            width: calc(100% - 160px) !important; /* 宽度计算，预留更多重置按钮空间 */
            z-index: 999 !important;            /* 确保在最上层 */
            background-color: transparent !important; /* 透明背景，继承系统主题 */
            max-width: calc(100% - 160px) !important; /* 最大宽度限制 */
        }
        
        /* 输入框本身：继承系统主题色 */
        div[data-testid="stChatInput"] input {
            width: calc(100% - 20px) !important; /* 输入框宽度，留出发送按钮空间 */
            height: 100% !important;            /* 占满容器高度 */
            padding: 1rem !important;           /* 统一的内边距 */
            background-color: var(--background-color) !important; /* 使用系统主题背景色 */
            border: 1px solid var(--primary-color) !important; /* 使用主题色作为边框 */
            border-radius: 4px !important;      /* 圆角边框 */
            color: var(--text-color) !important; /* 使用系统主题文字颜色 */
            font-size: 1rem !important;         /* 标准字体大小 */
            line-height: 1.5 !important;        /* 行高 */
            transition: all 0.3s ease !important; /* 平滑过渡效果 */
            margin-right: 20px !important;      /* 与发送按钮的间距 */
        }

        /* 输入框聚焦时的样式 */
        div[data-testid="stChatInput"] input:focus {
            outline: none !important;           /* 移除默认聚焦轮廓 */
            border-color: var(--primary-color) !important; /* 使用主题色 */
            box-shadow: 0 0 0 2px var(--primary-color-light) !important; /* 主题色阴影 */
        }

        /* 发送按钮容器 */
        div[data-testid="stChatInput"] button {
            right: 140px !important;           /* 与重置按钮保持距离 */
            background-color: var(--primary-color) !important; /* 使用主题色 */
            border-radius: 4px !important;     /* 圆角 */
            transition: all 0.3s ease !important; /* 过渡动画 */
        }
        
        /* ===== 重置按钮样式 ===== */
        /* 次要按钮：固定在右下角，跟随主题 */
        button[kind="secondary"] {
            position: fixed !important;          /* 固定定位 */
            bottom: 16px !important;            /* 距底部距离 */
            right: 20px !important;             /* 右侧留白 */
            z-index: 999 !important;            /* 确保在最上层 */
            margin: 0 !important;               /* 清除外边距 */
            width: 100px !important;            /* 减小固定宽度 */
            height: calc(1rem * 2 + 1.5em) !important; /* 与输入框等高 */
            background-color: var(--background-color) !important; /* 使用系统主题背景色 */
            border: 1px solid var(--primary-color) !important; /* 使用主题色边框 */
            color: var(--text-color) !important; /* 使用系统主题文字颜色 */
            border-radius: 4px !important;       /* 圆角 */
            transition: all 0.3s ease !important; /* 过渡动画 */
            min-width: 80px !important;          /* 最小宽度 */
            font-size: 0.9rem !important;        /* 稍微减小字体 */
            padding: 0 8px !important;           /* 减小内边距 */
        }

        /* 重置按钮悬停效果 */
        button[kind="secondary"]:hover {
            background-color: var(--primary-color-light) !important; /* 使用浅色主题色 */
            border-color: var(--primary-color) !important;
        }

        /* 在小屏幕上调整布局 */
        @media (max-width: 768px) {
            div[data-testid="stChatInput"] {
                width: calc(100% - 120px) !important; /* 减小输入框宽度 */
                max-width: calc(100% - 120px) !important;
            }
            
            div[data-testid="stChatInput"] button {
                right: 110px !important;        /* 调整发送按钮位置 */
            }
            
            button[kind="secondary"] {
                width: 80px !important;         /* 更小的重置按钮 */
                right: 10px !important;         /* 减小右侧间距 */
            }
        }
        
        /* ===== 主要按钮样式 ===== */
        /* 生成UML按钮：使用主题色 */
        button[kind="primary"] {
            background-color: var(--primary-color) !important; /* 使用主题色 */
            border: none !important;              /* 无边框 */
            color: white !important;              /* 白色文字 */
            padding: 0.5rem 1rem !important;      /* 内边距 */
            border-radius: 4px !important;        /* 圆角 */
            transition: all 0.3s ease !important; /* 颜色过渡动画 */
        }
        
        /* 主要按钮悬停效果 */
        button[kind="primary"]:hover {
            background-color: var(--primary-color-dark) !important; /* 使用深色主题色 */
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important; /* 添加阴影 */
        }
        
        /* ===== 布局调整 ===== */
        /* 主容器：为固定元素预留空间 */
        section.main > div.block-container {
            padding-bottom: calc(2rem + 1.5em) !important; /* 为输入框留出空间 */
            background-color: var(--background-color) !important; /* 使用系统主题背景色 */
        }

        /* ===== 欢迎页面样式 ===== */
        /* 大标题：AUG */
        .big-title {
            text-align: center;                   /* 居中对齐 */
            padding: 2rem 0;                      /* 上下内边距 */
            color: var(--primary-color);          /* 使用主题色 */
            font-size: 4rem;                      /* 大字体 */
            font-weight: bold;                    /*  */
            margin-top: 20vh;                     /* 顶部外边距 */
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2); /* 文字阴影 */
        }

        /* 副标题：AI UML Generator */
        .subtitle {
            text-align: center;                   /* 居中对齐 */
            color: var(--text-color-secondary);   /* 使���次要文字颜色 */
            font-size: 1.5rem;                    /* 中等字体 */
            margin-top: 1rem;                     /* 顶部外边距 */
        }
        </style>
    """, unsafe_allow_html=True)

    # 如果没有消息历史，显示大标题
    if not st.session_state.messages:
        st.markdown("""
            <div class="big-title">AUG</div>
            <div class="subtitle">Automantic UML Generator</div>
        """, unsafe_allow_html=True)
    else:
        # 显示所有历史消息
        for idx, message in enumerate(st.session_state.messages):
            create_message_container(message["role"], message["content"], idx)

    # 创建固定在底部的输入区域
    with st.container():
        prompt = st.chat_input("在这里输入您的消息...")
        if st.button("重置聊天", key="reset_button", type="secondary", on_click=reset_chat):
            pass

    if prompt:
        # 立即显示户输入
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # 添加到消息历史
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        messages_history = [
            {"role": "system", "content": "你是自动化需求建模工具AUG，你的任务是根据用户输入的案例进行需求分析和使用plantuml代码进行需求建模。用户会让你对生成的plantuml根据五大标准进行评价打分"},
        ] + st.session_state.messages

        try:
            # 显示加载状态
            with st.spinner('正在思考中...'):
                async def run_conversation():
                    try:
                        response = await get_bot_response(messages_history)
                        return response
                    except Exception as e:
                        return f"处理响应时出错: {str(e)}"

                # 运行异步任务
                final_response = asyncio.run(run_conversation())
                
                if final_response:
                    # 立即显示AI响应
                    with st.chat_message("assistant"):
                        st.markdown(final_response)
                    st.session_state.messages.append({"role": "assistant", "content": final_response})
                
                # 使用 rerun 重新加载页面
                st.rerun()

        except Exception as e:
            st.error(f"Error getting response from API: {str(e)}")

    # 添加处理编辑器消息的 JavaScript
    st.markdown("""
    <script>
    window.addEventListener('message', function(event) {
        if (event.data.type === 'uml-export') {
            // 更新编辑区域的内容
            const textArea = document.querySelector('textarea');
            if (textArea) {
                textArea.value = event.data.content;
                textArea.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()