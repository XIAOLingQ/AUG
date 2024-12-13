import streamlit as st
from stream.utils.uml import (
    get_existing_classes,
    get_name_mapping,
)

def render_class_diagram_editor(code_key, message_idx, current_code):
    """渲染类图编辑器"""
    # 类操作区域
    with st.expander("🔷 类操作", expanded=False):
        tabs = st.tabs(["添加类", "修改类", "删除类"])
        with tabs[0]:
            render_add_class(code_key, message_idx, current_code)
        with tabs[1]:
            render_modify_class(code_key, message_idx, current_code)
        with tabs[2]:
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
    
    # 检查类名是否已存在
    existing_classes = get_existing_classes(current_code)
    if class_name and class_name in existing_classes:
        st.error(f"类名 '{class_name}' 已存在")
        return
    
    # 属性数量选择
    attr_count = st.number_input(
        "属性数量",
        min_value=0,
        value=0,
        key=f"attr_count_input_{message_idx}"
    )
    
    # 方法数量选择
    method_count = st.number_input(
        "方法数量",
        min_value=0,
        value=0,
        key=f"method_count_input_{message_idx}"
    )
    
    # 属性列表
    attrs_list = []
    if attr_count > 0:
        st.subheader("属性列表")
        st.caption("可见性说明：+ 公有, - 私有, # 保护")
        
        # 表头
        cols = st.columns([1, 2, 2])
        with cols[0]:
            st.write("可见性")
        with cols[1]:
            st.write("属性名")
        with cols[2]:
            st.write("类型")
        
        # 属性输入行
        for i in range(attr_count):
            cols = st.columns([1, 2, 2])
            with cols[0]:
                visibility = st.selectbox(
                    "可见性",
                    ["+", "-", "#"],
                    key=f"attr_vis_{message_idx}_{i}",
                    label_visibility="collapsed"
                )
            with cols[1]:
                name = st.text_input(
                    "属性名",
                    key=f"attr_name_{message_idx}_{i}",
                    label_visibility="collapsed"
                )
            with cols[2]:
                type_ = st.text_input(
                    "类型",
                    key=f"attr_type_{message_idx}_{i}",
                    label_visibility="collapsed"
                )
            attrs_list.append({
                "visibility": visibility,
                "name": name,
                "type": type_
            })
    
    # 方法列表
    methods_list = []
    if method_count > 0:
        st.subheader("方法列表")
        st.caption("可见性说明：+ 公有, - 私有, # 保护")
        
        # 表头
        cols = st.columns([1, 2, 1, 2])
        with cols[0]:
            st.write("可见性")
        with cols[1]:
            st.write("方法名")
        with cols[2]:
            st.write("返回类型")
        with cols[3]:
            st.write("参数")
        
        # 方法输入行
        for i in range(method_count):
            cols = st.columns([1, 2, 1, 2])
            with cols[0]:
                visibility = st.selectbox(
                    "可见性",
                    ["+", "-", "#"],
                    key=f"method_vis_{message_idx}_{i}",
                    label_visibility="collapsed"
                )
            with cols[1]:
                name = st.text_input(
                    "方法名",
                    key=f"method_name_{message_idx}_{i}",
                    label_visibility="collapsed"
                )
            with cols[2]:
                return_type = st.text_input(
                    "返回类型",
                    key=f"method_return_{message_idx}_{i}",
                    label_visibility="collapsed"
                )
            with cols[3]:
                params = st.text_input(
                    "参数",
                    key=f"method_params_{message_idx}_{i}",
                    label_visibility="collapsed",
                    help="格式: param1: Type1, param2: Type2"
                )
            methods_list.append({
                "visibility": visibility,
                "name": name,
                "return_type": return_type,
                "params": params
            })
    
    # 添加到图表按钮
    if st.button("添加到图表", key=f"add_class_{message_idx}", type="primary"):
        if not class_name:
            st.error("请输入类名")
            return
            
        if class_name in get_existing_classes(current_code):
            st.error(f"类名 '{class_name}' 已存在")
            return
            
        lines = current_code.split('\n')
        new_class = f"\nclass {class_name} {{\n"
        
        # 添加属性
        for attr in attrs_list:
            if attr["name"].strip():
                new_class += f"  {attr['visibility']}{attr['name']}"
                if attr["type"].strip():
                    new_class += f": {attr['type']}"
                new_class += "\n"
        
        # 添加方法
        for method in methods_list:
            if method["name"].strip():
                new_class += f"  {method['visibility']}{method['name']}"
                new_class += "("
                if method["params"].strip():
                    new_class += method["params"]
                new_class += ")"
                if method["return_type"].strip():
                    new_class += f": {method['return_type']}"
                new_class += "\n"
        
        new_class += "}\n"
        
        insert_pos = next(i for i, line in enumerate(lines) 
            if '@enduml' in line.lower())
        lines.insert(insert_pos, new_class)
        st.session_state[code_key] = '\n'.join(lines)
        st.success(f"类 '{class_name}' 已添加")
        st.rerun()

def render_modify_class(code_key, message_idx, current_code):
    """渲染修改类界面"""
    existing_classes = get_existing_classes(current_code)
    if not existing_classes:
        st.info("没有可修改的类")
        return
        
    class_to_modify = st.selectbox(
        "选择要修改的类",
        options=existing_classes,
        key=f"modify_class_{message_idx}"
    )
    
    # 当选择的类发生变化时，重置 session state
    if f"last_modified_class_{message_idx}" not in st.session_state:
        st.session_state[f"last_modified_class_{message_idx}"] = class_to_modify
    elif st.session_state[f"last_modified_class_{message_idx}"] != class_to_modify:
        # 清除之前的属性和方法列表
        if f"modify_attrs_list_{message_idx}" in st.session_state:
            del st.session_state[f"modify_attrs_list_{message_idx}"]
        if f"modify_methods_list_{message_idx}" in st.session_state:
            del st.session_state[f"modify_methods_list_{message_idx}"]
        st.session_state[f"last_modified_class_{message_idx}"] = class_to_modify
    
    # 解析当前类的信息
    lines = current_code.split('\n')
    class_content = []
    in_class = False
    for line in lines:
        if line.strip().startswith(f'class {class_to_modify}'):
            in_class = True
            continue
        if in_class:
            if line.strip() == '}':
                break
            if line.strip():
                class_content.append(line.strip())
    
    # 分离属性和方法
    attributes = []
    methods = []
    for item in class_content:
        if '(' in item:  # 方法
            vis = item[0] if item[0] in ['+', '-', '#'] else '+'
            name = item[1:item.index('(')] if item[0] in ['+', '-', '#'] else item[:item.index('(')]
            params = item[item.index('(')+1:item.index(')')]
            return_type = item[item.index(')')+2:] if ': ' in item else ""
            methods.append({
                "visibility": vis,
                "name": name.strip(),
                "return_type": return_type,
                "params": params
            })
        else:  # 属性
            vis = item[0] if item[0] in ['+', '-', '#'] else '+'
            try:
                name = item[1:item.index(': ')] if ': ' in item else item[1:]
                type_ = item[item.index(': ')+2:] if ': ' in item else ""
            except:
                # 处理特殊情况
                name = item[1:] if item else ""
                type_ = ""
            attributes.append({
                "visibility": vis,
                "name": name.strip(),
                "type": type_
            })
    
    # 初始化session state（仅在首次加载时）
    if f"modify_attrs_list_{message_idx}" not in st.session_state:
        st.session_state[f"modify_attrs_list_{message_idx}"] = attributes
    if f"modify_methods_list_{message_idx}" not in st.session_state:
        st.session_state[f"modify_methods_list_{message_idx}"] = methods
    
    new_class_name = st.text_input("新类名", value=class_to_modify, key=f"new_class_name_{message_idx}")
    
    # 属性列表
    st.subheader("属性列表")
    attrs_list = st.session_state[f"modify_attrs_list_{message_idx}"]
    
    cols = st.columns([1, 2, 2, 1])
    with cols[0]:
        st.write("可见性")
    with cols[1]:
        st.write("属性名")
    with cols[2]:
        st.write("类型")
    
    for i, attr in enumerate(attrs_list):
        cols = st.columns([1, 2, 2, 1])
        with cols[0]:
            attrs_list[i]["visibility"] = st.selectbox(
                "可见性",
                ["+", "-", "#"],
                key=f"modify_attr_vis_{message_idx}_{i}",
                label_visibility="collapsed",
                index=["+", "-", "#"].index(attr["visibility"])
            )
        with cols[1]:
            attrs_list[i]["name"] = st.text_input(
                "属性名",
                value=attr["name"],
                key=f"modify_attr_name_{message_idx}_{i}",
                label_visibility="collapsed"
            )
        with cols[2]:
            attrs_list[i]["type"] = st.text_input(
                "类型",
                value=attr["type"],
                key=f"modify_attr_type_{message_idx}_{i}",
                label_visibility="collapsed"
            )
        with cols[3]:
            if st.button("删除", key=f"modify_del_attr_{message_idx}_{i}"):
                attrs_list.pop(i)
                st.session_state[f"modify_attrs_list_{message_idx}"] = attrs_list
                st.rerun()
    
    if st.button("添加属性", key=f"modify_add_attr_{message_idx}"):
        attrs_list.append({"visibility": "+", "name": "", "type": ""})
        st.session_state[f"modify_attrs_list_{message_idx}"] = attrs_list
        st.rerun()
    
    # 方法列表
    st.subheader("方法列表")
    methods_list = st.session_state[f"modify_methods_list_{message_idx}"]
    
    cols = st.columns([1, 2, 1, 2, 1])
    with cols[0]:
        st.write("可见性")
    with cols[1]:
        st.write("方法名")
    with cols[2]:
        st.write("返回类型")
    with cols[3]:
        st.write("参数")
    
    for i, method in enumerate(methods_list):
        cols = st.columns([1, 2, 1, 2, 1])
        with cols[0]:
            methods_list[i]["visibility"] = st.selectbox(
                "可见性",
                ["+", "-", "#"],
                key=f"modify_method_vis_{message_idx}_{i}",
                label_visibility="collapsed",
                index=["+", "-", "#"].index(method["visibility"])
            )
        with cols[1]:
            methods_list[i]["name"] = st.text_input(
                "方法名",
                value=method["name"],
                key=f"modify_method_name_{message_idx}_{i}",
                label_visibility="collapsed"
            )
        with cols[2]:
            methods_list[i]["return_type"] = st.text_input(
                "返回类型",
                value=method["return_type"],
                key=f"modify_method_return_{message_idx}_{i}",
                label_visibility="collapsed"
            )
        with cols[3]:
            methods_list[i]["params"] = st.text_input(
                "参数",
                value=method["params"],
                key=f"modify_method_params_{message_idx}_{i}",
                label_visibility="collapsed",
                help="格式: param1: Type1, param2: Type2"
            )
        with cols[4]:
            if st.button("删除", key=f"modify_del_method_{message_idx}_{i}"):
                methods_list.pop(i)
                st.session_state[f"modify_methods_list_{message_idx}"] = methods_list
                st.rerun()
    
    if st.button("添加方法", key=f"modify_add_method_{message_idx}"):
        methods_list.append({"visibility": "+", "name": "", "return_type": "", "params": ""})
        st.session_state[f"modify_methods_list_{message_idx}"] = methods_list
        st.rerun()
    
    if st.button("保存修改", key=f"save_modify_{message_idx}", type="primary"):
        # 删除原有类定义
        new_lines = []
        skip_class = False
        relationships = []  # 存储所有关系
        
        for line in lines:
            line_stripped = line.strip()
            
            # 跳过原有类定义
            if line_stripped.startswith(f'class {class_to_modify}'):
                skip_class = True
                continue
            if skip_class and line_stripped == '}':
                skip_class = False
                continue
            
            # 收集并暂时跳过相关关系
            # 检查是否包含类名（带引号或不带引号）
            class_patterns = [
                f'"{class_to_modify}"',  # 带引号
                f' {class_to_modify} ',  # 不带引号，两边有空格
                f' {class_to_modify}(',  # 不带引号，后面跟括号
                f'^{class_to_modify} ',  # 不带引号，行首
                f' {class_to_modify}$'   # 不带引号，行尾
            ]
            if any(pattern in f" {line_stripped} " for pattern in class_patterns):
                relationships.append(line)
                continue
            
            if not skip_class:
                new_lines.append(line)
        
        # 添加修改后的类
        new_class = f"\nclass {new_class_name} {{\n"
        
        # 添加属性
        for attr in attrs_list:
            if attr["name"].strip():
                new_class += f"  {attr['visibility']}{attr['name']}"
                if attr["type"].strip():
                    new_class += f": {attr['type']}"
                new_class += "\n"
        
        # 添加方法
        for method in methods_list:
            if method["name"].strip():
                new_class += f"  {method['visibility']}{method['name']}"
                new_class += "("
                if method["params"].strip():
                    new_class += method["params"]
                new_class += ")"
                if method["return_type"].strip():
                    new_class += f": {method['return_type']}"
                new_class += "\n"
        
        new_class += "}\n"
        
        # 添���新类
        insert_pos = next(i for i, line in enumerate(new_lines) 
            if '@enduml' in line.lower())
        new_lines.insert(insert_pos, new_class)
        
        # 更新并添加关系
        for relationship in relationships:
            updated_relationship = relationship
            
            # 处理类名在关系定义的情况
            if any(rel in relationship for rel in ['<|--', '--|>', '--', '--*', '*--', '--o', 'o--']):
                # 保持原有的引号状态
                if f'"{class_to_modify}"' in relationship:
                    updated_relationship = relationship.replace(f'"{class_to_modify}"', f'"{new_class_name}"')
                else:
                    updated_relationship = relationship.replace(f' {class_to_modify} ', f' {new_class_name} ')
                    updated_relationship = updated_relationship.replace(f' {class_to_modify}(', f' {new_class_name}(')
                    updated_relationship = updated_relationship.replace(f'^{class_to_modify} ', f'{new_class_name} ')
                    updated_relationship = updated_relationship.replace(f' {class_to_modify}$', f' {new_class_name}')
            
            new_lines.insert(insert_pos, updated_relationship)
        
        st.session_state[code_key] = '\n'.join(new_lines)
        
        # 清除修改状态
        if f"modify_attrs_list_{message_idx}" in st.session_state:
            del st.session_state[f"modify_attrs_list_{message_idx}"]
        if f"modify_methods_list_{message_idx}" in st.session_state:
            del st.session_state[f"modify_methods_list_{message_idx}"]
        
        st.success(f"类 '{class_to_modify}' 已修改为 '{new_class_name}'")
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
    name_map = get_name_mapping(current_code)  # 获取名称映射
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
        
        # 添加关系多重性选项
        source_multiplicity = st.text_input("源类多重性(可选，如: 1, 0..*, 1..*)", key=f"source_mult_{message_idx}")
        target_multiplicity = st.text_input("目标类多重性(可选，如: 1, 0..*, 1..*)", key=f"target_mult_{message_idx}")
        
        label = st.text_input("关系标签(可选)", key=f"label_{message_idx}")
        
        if st.button("添加关系", key=f"add_relation_{message_idx}", type="primary"):
            lines = current_code.split('\n')
            
            # 获取源和目标的别名（如果有）
            source_alias = next((alias for alias, name in name_map.items() if name == source), source)
            target_alias = next((alias for alias, name in name_map.items() if name == target), target)
            
            # 构建关系字符串
            relation_parts = []
            relation_parts.append(f'"{source_alias}"')
            if source_multiplicity.strip():
                relation_parts.append(f'"{source_multiplicity}"')
            relation_parts.append(relation[0])
            if target_multiplicity.strip():
                relation_parts.append(f'"{target_multiplicity}"')
            relation_parts.append(f'"{target_alias}"')
            
            relation_str = ' '.join(relation_parts)
            if label.strip():
                relation_str += f' : {label}'
            relation_str += '\n'
            
            # 找到所有类定义的开始和结束位置
            class_positions = []  # 存储每个类的开始和结束位置
            in_class = False
            class_start = -1
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                if line_stripped.startswith('class '):
                    in_class = True
                    class_start = i
                elif line_stripped == '}' and in_class:
                    in_class = False
                    class_positions.append((class_start, i))
            
            # 找到第一个独立的属性或方法定义的位置（在类定义之外的）
            method_start_pos = len(lines)
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                # 确保不在任何类定义内部
                if not any(start <= i <= end for start, end in class_positions):
                    if (line_stripped.startswith('+') or 
                        line_stripped.startswith('-') or 
                        line_stripped.startswith('#')) or \
                       ('(' in line_stripped and ')' in line_stripped):
                        method_start_pos = i
                        break
            
            # 选择合适的插入位置：在最后一个类定义之后，但在第一个独立方法/属性之前
            if class_positions:
                last_class_end = max(pos[1] for pos in class_positions)
                insert_pos = min(last_class_end + 1, method_start_pos)
                
                # 确保插入位置不在任何类的内部
                while any(start <= insert_pos <= end for start, end in class_positions):
                    insert_pos = max(pos[1] + 1 for pos in class_positions if pos[1] >= insert_pos)
            else:
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
            # 检查是否包含类名和关系符号
            has_class = any(f'"{c}"' in line_stripped or f' {c} ' in line_stripped 
                          or line_stripped.startswith(f'{c} ')
                          or line_stripped.endswith(f' {c}')
                          for c in existing_classes)
            
            # 检查是否包含关系符号
            has_relation = any(rel in line_stripped for rel in [
                '--', '--|>', '<|--', '--*', '*--', '--o', 'o--'
            ])
            
            if has_class and has_relation:
                # 移除多余的空格并标准化空格
                normalized_line = ' '.join(line_stripped.split())
                if normalized_line not in relations:  # 避免重复
                    relations.append(normalized_line)
        
        if relations:
            relation_to_delete = st.selectbox(
                "选择要删除的关系",
                options=relations,
                key=f"delete_relation_{message_idx}",
                format_func=lambda x: (x.replace(" --|> ", " ⯈ ")
                                     .replace(" --* ", " ◆ ")
                                     .replace(" --o ", " ◇ ")
                                     .replace(" <|-- ", " ⯇ ")
                                     .replace(" *-- ", " ◆ ")
                                     .replace(" o-- ", " ◇ ")
                                     .replace(" -- ", " — "))
            )
            
            if st.button("删除关系", key=f"delete_relation_btn_{message_idx}", type="primary"):
                # 标准化要删除的关系
                normalized_to_delete = ' '.join(relation_to_delete.split())
                # 保留不匹配的行
                new_lines = [line for line in lines 
                           if ' '.join(line.strip().split()) != normalized_to_delete]
                
                st.session_state[code_key] = '\n'.join(new_lines)
                st.success("关系已删除")
                st.rerun()
        else:
            st.info("没有可删除的关系")
    else:
        st.info("请先添加至少一个类")