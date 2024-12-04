import streamlit as st
from stream.utils.uml import get_uml_diagram, get_diagram_type
from stream.components.editors.class_editor import render_class_diagram_editor
from stream.components.editors.usecase_editor import render_usecase_diagram_editor
from stream.components.editors.sequence_editor import render_sequence_diagram_editor

def render_uml_editor(code_key, message_idx):
    """渲染 UML 编辑器组件"""
    current_code = st.session_state[code_key]
    
    # 添加样式
    st.markdown("""
        <style>
        div[data-testid="stImage"] {
            max-width: 600px !important;
            margin: 0 auto !important;
        }
        
        div[data-testid="stExpander"] {
            background-color: #1E1E1E;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        
        .download-button {
            display: inline-block;
            background-color: #1E88E5;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-align: center;
            margin-top: 10px;
            width: 120px;
        }
        
        .stTextArea textarea {
            font-family: monospace;
            font-size: 14px;
            line-height: 1.4;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 创建两列布局
    edit_col, preview_col = st.columns([0.5, 0.5])
    
    with edit_col:
        st.subheader("UML 编辑器")
        
        # 添加编辑模式切换
        edit_mode = st.radio(
            "编辑模式",
            ["可视化编辑", "代码编辑"],
            horizontal=True,
            key=f"edit_mode_{message_idx}"
        )
        
        if edit_mode == "代码编辑":
            # 直接编辑 PlantUML 代码
            new_code = st.text_area("PlantUML 代码", current_code, height=400)
            if new_code != current_code:
                st.session_state[code_key] = new_code
                current_code = new_code
        else:
            # 可视化编辑器
            # 根据图表类型选择对应的编辑器
            diagram_type = get_diagram_type(current_code)
            if diagram_type == "class":
                render_class_diagram_editor(code_key, message_idx, current_code)
            elif diagram_type == "usecase":
                render_usecase_diagram_editor(code_key, message_idx, current_code)
            elif diagram_type == "sequence":
                render_sequence_diagram_editor(code_key, message_idx, current_code)
            else:
                st.warning("未识别的图表类型")
    
    with preview_col:
        st.subheader("预览")
        # 显示当前的 PlantUML 代码
        with st.expander("📝 查看 PlantUML 代码", expanded=False):
            st.code(current_code, language='java')
            
        # 显示图像预览
        diagram_data = get_uml_diagram(current_code)
        if diagram_data:
            st.image(diagram_data['url'], width=600)
            
            # 下载按钮
            download_filename = f"uml_diagram_{message_idx}.{diagram_data['format']}"
            download_link = f'''
            <div style="text-align: center;">
                <a href="data:image/{diagram_data["format"]};base64,{diagram_data["data"]}" 
                   download="{download_filename}">
                    <button class="download-button">下载图表</button>
                </a>
            </div>
            '''
            st.markdown(download_link, unsafe_allow_html=True)
        else:
            st.error("生成UML图失败，请检查代码语法")