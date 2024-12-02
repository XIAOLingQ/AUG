import streamlit as st
import uuid
from zhipuai import ZhipuAI
from plantuml import PlantUML
import re

# Constants
plantuml = PlantUML(url='http://www.plantuml.com/plantuml/png/')
DEFAULT_USER_ID = str(uuid.uuid4())

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Page config
st.set_page_config(page_title="Chat Application", layout="wide")

def get_uml_diagram(uml_code):
    """Generate PlantUML diagram URL using public server"""
    try:
        url = plantuml.get_url(uml_code)
        return url
    except Exception as e:
        st.error(f"Error generating UML diagram: {str(e)}")
        return None

def reset_chat():
    """Reset chat history"""
    st.session_state.messages = []
    st.rerun()

def create_message_container(role, content):
    # 移除 chat_message 的 key 参数
    with st.chat_message(role):
        parts = re.split(r'(```[\s\S]*?```)', content, flags=re.DOTALL)
        for i, part in enumerate(parts):
            stripped_part = part.strip()
            if stripped_part.startswith('```') and stripped_part.endswith('```'):
                # 使用消息索引和时间戳创建唯一的key
                message_index = len(st.session_state.messages)
                timestamp = uuid.uuid4().hex[:8]  # 添加一个随机字符串来确保唯一性
                code_key = f"code_{role}_{message_index}_{i}_{timestamp}"
                editor_key = f"editor_{code_key}"
                
                # 保留完整的代码块，包括语言标记
                code = stripped_part.strip('`').strip()
                first_line = code.split('\n')[0] if '\n' in code else ''
                
                # 如果是 PlantUML 代码，移除第一行的标记
                if first_line.lower() in ['plantuml', 'uml']:
                    code = '\n'.join(code.split('\n')[1:])
                
                if code_key not in st.session_state:
                    st.session_state[code_key] = code
                
                # 计算代码行数并设置适当的高度
                num_lines = len(code.split('\n'))
                height = max(num_lines * 24, 100)  # 每行大约24像素，最小高度100像素
                
                # 使用 st.text_area 显示可编辑的代码块
                edited_code = st.text_area(
                    "编辑代码",
                    value=st.session_state[code_key],
                    key=editor_key,  # 使用新的唯key
                    height=height  # 根据代码行数动态设置高度
                )
                
                # 如果代码被修改，更新session state
                if edited_code != st.session_state[code_key]:
                    st.session_state[code_key] = edited_code
                
                # 如果是 PlantUML 代码，处理 UML 图生成
                if first_line.lower() in ['plantuml', 'uml']:
                    if '@startuml' in edited_code.lower() and '@enduml' in edited_code.lower():
                        diagram_key = f"diagram_{role}_{message_index}_{i}"
                        toggle_key = f"toggle_{diagram_key}"
                        
                        # 初始化 toggle 状态
                        if toggle_key not in st.session_state:
                            st.session_state[toggle_key] = True
                        
                        # 使用更简单的方式处理toggle状态
                        show_diagram = st.toggle(
                            '显示/隐藏 UML 图',
                            key=toggle_key  # Streamlit 会自动处理状态
                        )
                        
                        if show_diagram:
                            try:
                                diagram_url = get_uml_diagram(edited_code)
                                if diagram_url:
                                    st.image(diagram_url, caption="Generated UML Diagram")
                                else:
                                    st.error("生成UML图失败，请检查PlantUML语法")
                            except Exception as e:
                                st.error(f"生成UML图时发生错误: {str(e)}")
            else:
                if stripped_part:
                    # 移除 key 参数，直接显示文本内容
                    st.markdown(stripped_part)

def main():
    st.markdown("""
        <style>
        /* 输入框容器样式 */
        div[data-testid="stChatInput"] {
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            padding: 1rem !important;
            width: calc(100% - 160px) !important;
            background-color: #0E1117 !important;
            z-index: 999 !important;
        }
        
        /* 重置按钮样式 - 只针对 secondary 类型的按钮 */
        button[kind="secondary"] {
            position: fixed !important;
            bottom: 16px !important;
            right: 0 !important;
            z-index: 999 !important;
            margin: 0 !important;
            width: 120px !important;
            background-color: #262730 !important;
            border: 1px solid #4a4a4a !important;
            color: white !important;
        }
        
        /* 生成UML按钮样式 - 针对 primary 类型的按钮 */
        button[kind="primary"] {
            background-color: #1E88E5 !important;
            border: none !important;
            color: white !important;
            padding: 0.5rem 1rem !important;
            border-radius: 4px !important;
            transition: background-color 0.3s !important;
        }
        
        button[kind="primary"]:hover {
            background-color: #1976D2 !important;
        }
        
        /* 为底部固定元素留出空间 */
        section.main > div.block-container {
            padding-bottom: 80px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # 显示历史消息
    for message in st.session_state.messages:
        create_message_container(message["role"], message["content"])

    # 创建固定在底部的输入区域
    with st.container():
        prompt = st.chat_input("在这里输入您的消息...")
        st.button("重置聊天", key="reset_button", type="secondary")

    if prompt:
        # Add user message
        create_message_container("user", prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get bot response
        full_response = ""
        
        client = ZhipuAI(api_key="9e552efc10638d85e8042d40b9acbcce.jissfQ9lXpIbJRfK")

        messages_history = [
            {"role": "system", "content": "你是一个乐于解答各种问题的助手，你的任务是为用户提供专业、准确、有见地的建议。"},
        ] + st.session_state.messages
        
        messages_history.append({"role": "user", "content": prompt})

        try:
            response = client.chat.completions.create(
                model="glm-4-9b",
                messages=messages_history,
                top_p=0.7,
                temperature=0.95,
                max_tokens=1024,
                tools=[{"type": "web_search", "web_search": {"search_result": True}}],
                stream=True
            )
            
            # 创建一个占位符用于流式显示
            placeholder = st.empty()
            with placeholder.container():
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    for trunk in response:
                        try:
                            content = trunk.choices[0].delta.content if trunk.choices else ""
                            full_response += content
                            message_placeholder.markdown(full_response + "▌")
                        except Exception as e:
                            st.error(f"Error processing response: {str(e)}")
                            break
            
            # 清除流式显示的内容
            placeholder.empty()
            
            # 显示最终的完整响应
            create_message_container("assistant", full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error getting response from ZhipuAI: {str(e)}")

if __name__ == "__main__":
    main()