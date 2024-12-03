import streamlit as st
from stream.utils.uml import get_existing_classes

def render_class_diagram_editor(code_key, message_idx, current_code):
    """渲染类图编辑器"""
    # 类操作区域
    with st.expander("🔷 类操作", expanded=False):
        tabs = st.tabs(["添加类", "删除类"])
        with tabs[0]:
            render_add_class(code_key, message_idx, current_code)
        with tabs[1]:
            render_delete_class(code_key, message_idx, current_code)
    
    # 关系操作区域
    with st.expander("🔗 关系操作", expanded=False):
        tabs = st.tabs(["添加关系", "删除关系"])
        with tabs[0]:
            render_add_relationship(code_key, message_idx, current_code)
        with tabs[1]:
            render_delete_relationship(code_key, message_idx, current_code)

def render_add_class(code_key, message_idx, current_code):
    """渲染添加类界面"""
    class_name = st.text_input("类名", key=f"class_name_{message_idx}")
    attributes = st.text_area(
        "属性 (每行一个)", 
        height=100,
        key=f"attrs_{message_idx}", 
        help="格式: +name: String"
    )
    methods = st.text_area(
        "方法 (每行一个)", 
        height=100,
        key=f"methods_{message_idx}", 
        help="格式: +getName(): String"
    )
    
    if st.button("添加到图表", key=f"add_class_{message_idx}", type="primary"):
        lines = current_code.split('\n')
        new_class = f"\nclass {class_name} {{\n"
        for attr in attributes.split('\n'):
            if attr.strip():
                new_class += f"  {attr.strip()}\n"
        for method in methods.split('\n'):
            if method.strip():
                new_class += f"  {method.strip()}\n"
        new_class += "}\n"
        
        insert_pos = next(i for i, line in enumerate(lines) 
            if '@enduml' in line.lower())
        lines.insert(insert_pos, new_class)
        st.session_state[code_key] = '\n'.join(lines)
        st.success(f"类 '{class_name}' 已添加")
        st.rerun()

def render_delete_class(code_key, message_idx, current_code):
    """渲染删除类界面"""
    existing_classes = get_existing_classes(current_code)
    if existing_classes:
        class_to_delete = st.selectbox(
            "选择要删除的类",
            options=existing_classes,
            key=f"delete_class_{message_idx}"
        )
        
        if st.button("删除类", key=f"delete_class_btn_{message_idx}", type="primary"):
            lines = current_code.split('\n')
            new_lines = []
            skip_class = False
            class_found = False
            
            for line in lines:
                line_stripped = line.strip()
                
                if line_stripped.startswith(f'class {class_to_delete}'):
                    skip_class = True
                    class_found = True
                    continue
                
                if skip_class and line_stripped == '}':
                    skip_class = False
                    continue
                
                if any(pattern.format(class_to_delete) in line_stripped for pattern in [
                    '{}', '{}--', '--{}', '{}--|>', '<|--{}', '{}--*', '*--{}', '{}--o', 'o--{}'
                ]):
                    continue
                
                if not skip_class:
                    new_lines.append(line)
            
            if class_found:
                st.session_state[code_key] = '\n'.join(new_lines)
                st.success(f"类 '{class_to_delete}' 及其相关关系已被删除")
                st.rerun()
            else:
                st.error(f"未找到类 '{class_to_delete}'")
    else:
        st.info("没有可删除的类")

def render_add_relationship(code_key, message_idx, current_code):
    """渲染添加关系界面"""
    existing_classes = get_existing_classes(current_code)
    if existing_classes:
        source = st.selectbox(
            "源类",
            options=existing_classes,
            key=f"source_{message_idx}"
        )
        
        relation = st.selectbox(
            "关系类型", 
            [
                ("--", "关联"),
                ("--|>", "继承"),
                ("--*", "组合"),
                ("--o", "聚合"),
                ("<|--", "反向继承"),
                ("*--", "反向组合"),
                ("o--", "反向聚合")
            ],
            format_func=lambda x: f"{x[0]} ({x[1]})",
            key=f"relation_{message_idx}"
        )
        
        target = st.selectbox(
            "目标类",
            options=existing_classes,
            key=f"target_{message_idx}"
        )
        
        label = st.text_input("关系标签(可选)", key=f"label_{message_idx}")
        
        if st.button("添加关系", key=f"add_relation_{message_idx}", type="primary"):
            lines = current_code.split('\n')
            relation_str = f"{source} {relation[0]} {target}"
            if label.strip():
                relation_str += f" : {label}"
            relation_str += "\n"
            
            insert_pos = next(i for i, line in enumerate(lines) 
                if '@enduml' in line.lower())
            lines.insert(insert_pos, relation_str)
            st.session_state[code_key] = '\n'.join(lines)
            st.success("关系已添加")
            st.rerun()
    else:
        st.info("请先添加至少一个类")

def render_delete_relationship(code_key, message_idx, current_code):
    """渲染删除关系界面"""
    existing_classes = get_existing_classes(current_code)
    if existing_classes:
        relations = []
        lines = current_code.split('\n')
        for line in lines:
            line_stripped = line.strip()
            if any(rel[0] in line_stripped for rel in [
                ("--", "关联"),
                ("--|>", "继承"),
                ("--*", "组合"),
                ("--o", "聚合"),
                ("<|--", "反向继承"),
                ("*--", "反向组合"),
                ("o--", "反向聚合")
            ]):
                parts = line_stripped.split()
                if len(parts) >= 3 and any(c in existing_classes for c in parts):
                    relations.append(line_stripped)
        
        if relations:
            relation_to_delete = st.selectbox(
                "选择要删除的关系",
                options=relations,
                key=f"delete_relation_{message_idx}",
                format_func=lambda x: x.replace("--", " → ").replace("|>", "继承").replace("*", "组合").replace("o", "聚合")
            )
            
            if st.button("删除关系", key=f"delete_relation_btn_{message_idx}", type="primary"):
                new_lines = [line for line in lines if line.strip() != relation_to_delete]
                st.session_state[code_key] = '\n'.join(new_lines)
                st.success("关系已删除")
                st.rerun()
        else:
            st.info("没有可删除的关系")
    else:
        st.info("请先添加至少一个类")