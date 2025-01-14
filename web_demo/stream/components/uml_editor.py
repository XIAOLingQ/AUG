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
        /* ===== 按钮基础样式 ===== */
        button[kind] {
            background-color: var(--primary-color) !important;
            color: #FFD700 !important;  /* 金黄色文字 */
            font-weight: bold !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            border-radius: 4px !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            text-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;  /* 轻微文字阴影提升可读性 */
        }
        
        /* 按钮悬停效果 */
        button[kind]:hover {
            background-color: #4CAF50 !important;  /* 绿色背景 */
            color: #FFD700 !important;  /* 保持金黄色文字 */
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
            transform: translateY(-1px) !important;
        }
        
        /* 下载按钮样式 */
        .download-button {
            display: inline-block;
            background-color: var(--primary-color) !important;
            color: #FFD700 !important;  /* 金黄色文字 */
            font-weight: bold !important;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-align: center;
            margin-top: 10px;
            width: 120px;
            transition: all 0.3s ease;
            text-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
        }
        
        /* 下载按钮悬停效果 */
        .download-button:hover {
            background-color: #4CAF50 !important;  /* 绿色背景 */
            color: #FFD700 !important;  /* 保持金黄色文字 */
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            transform: translateY(-1px);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 创建两列布局
    edit_col, preview_col = st.columns([0.5, 0.5])
    
    with edit_col:
        st.subheader("UML Editor")
        
        edit_mode_key = f"edit_mode_{code_key}_{message_idx}"
        edit_mode = st.radio(
            "Edit Mode",
            ["Visual Edit", "Code Edit"],
            horizontal=True,
            key=edit_mode_key
        )
        
        if edit_mode == "Code Edit":
            # 代码编辑模式
            text_area_key = f"text_area_{code_key}_{message_idx}"
            new_code = st.text_area(
                "PlantUML Code", 
                current_code, 
                height=400,
                key=text_area_key,
                kwargs={"id": f"textarea_{text_area_key}"}
            )
            
            # 检查代码是否发生变化
            if new_code != current_code:
                st.session_state[code_key] = new_code
                # 立即重新渲染图表
                diagram_data = get_uml_diagram(new_code)
                if diagram_data:
                    st.rerun()
        else:
            # 可视化编辑器
            diagram_type = get_diagram_type(current_code)
            if diagram_type == "class":
                render_class_diagram_editor(code_key, message_idx, current_code)
            elif diagram_type == "usecase":
                render_usecase_diagram_editor(code_key, message_idx, current_code)
            elif diagram_type == "sequence":
                render_sequence_diagram_editor(code_key, message_idx, current_code)
            else:
                st.warning("Unrecognized diagram type")
    
    # 预览列
    with preview_col:
        st.subheader("Preview")
        # 显示当前的 PlantUML 代码
        with st.expander("📝 View PlantUML Code", expanded=False):
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
                    <button class="download-button">Download Diagram</button>
                </a>
            </div>
            '''
            st.markdown(download_link, unsafe_allow_html=True)
        else:
            st.error("Failed to generate UML diagram, please check the code syntax")