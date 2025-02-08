import streamlit as st
from utils.uml import (
    get_existing_classes,
    get_name_mapping,
)

def render_class_diagram_editor(code_key, message_idx, current_code):
    """Render class diagram editor"""
    # Class operations area
    with st.expander("🔷 Class Operations", expanded=False):
        tabs = st.tabs(["Add Class", "Modify Class", "Delete Class"])
        with tabs[0]:
            render_add_class(code_key, message_idx, current_code)
        with tabs[1]:
            render_modify_class(code_key, message_idx, current_code)
        with tabs[2]:
            render_delete_class(code_key, message_idx, current_code)
    
    # Relationship operations area
    with st.expander("🔗 Relationship Operations", expanded=False):
        tabs = st.tabs(["Add Relationship", "Delete Relationship"])
        with tabs[0]:
            render_add_relationship(code_key, message_idx, current_code)
        with tabs[1]:
            render_delete_relationship(code_key, message_idx, current_code)

def render_add_class(code_key, message_idx, current_code):
    """Render add class interface"""
    class_name = st.text_input("Class Name", key=f"class_name_{message_idx}")
    
    # Check if class name already exists
    existing_classes = get_existing_classes(current_code)
    if class_name and class_name in existing_classes:
        st.error(f"Class name '{class_name}' already exists")
        return
    
    # Attribute count selection
    attr_count = st.number_input(
        "Number of Attributes",
        min_value=0,
        value=0,
        key=f"attr_count_input_{message_idx}"
    )
    
    # Method count selection
    method_count = st.number_input(
        "Number of Methods",
        min_value=0,
        value=0,
        key=f"method_count_input_{message_idx}"
    )
    
    # Attribute list
    attrs_list = []
    if attr_count > 0:
        st.subheader("Attribute List")
        st.caption("Visibility: + Public, - Private, # Protected")
        
        # Table header
        cols = st.columns([1, 2, 2])
        with cols[0]:
            st.write("Visibility")
        with cols[1]:
            st.write("Name")
        with cols[2]:
            st.write("Type")
        
        # Attribute input row
        for i in range(attr_count):
            cols = st.columns([1, 2, 2])
            with cols[0]:
                visibility = st.selectbox(
                    "Visibility",
                    ["+", "-", "#"],
                    key=f"attr_vis_{message_idx}_{i}",
                    label_visibility="collapsed"
                )
            with cols[1]:
                name = st.text_input(
                    "Name",
                    key=f"attr_name_{message_idx}_{i}",
                    label_visibility="collapsed"
                )
            with cols[2]:
                type_ = st.text_input(
                    "Type",
                    key=f"attr_type_{message_idx}_{i}",
                    label_visibility="collapsed"
                )
            attrs_list.append({
                "visibility": visibility,
                "name": name,
                "type": type_
            })
    
    # Method list
    methods_list = []
    if method_count > 0:
        st.subheader("Method List")
        st.caption("Visibility: + Public, - Private, # Protected")
        
        # Table header
        cols = st.columns([1, 2, 1, 2])
        with cols[0]:
            st.write("Visibility")
        with cols[1]:
            st.write("Method Name")
        with cols[2]:
            st.write("Return Type")
        with cols[3]:
            st.write("Parameters")
        
        # Method input row
        for i in range(method_count):
            cols = st.columns([1, 2, 1, 2])
            with cols[0]:
                visibility = st.selectbox(
                    "Visibility",
                    ["+", "-", "#"],
                    key=f"method_vis_{message_idx}_{i}",
                    label_visibility="collapsed"
                )
            with cols[1]:
                name = st.text_input(
                    "Method Name",
                    key=f"method_name_{message_idx}_{i}",
                    label_visibility="collapsed"
                )
            with cols[2]:
                return_type = st.text_input(
                    "Return Type",
                    key=f"method_return_{message_idx}_{i}",
                    label_visibility="collapsed"
                )
            with cols[3]:
                params = st.text_input(
                    "Parameters",
                    key=f"method_params_{message_idx}_{i}",
                    label_visibility="collapsed",
                    help="Format: param1: Type1, param2: Type2"
                )
            methods_list.append({
                "visibility": visibility,
                "name": name,
                "return_type": return_type,
                "params": params
            })
    
    # Add to diagram button
    if st.button("Add to Diagram", key=f"add_class_{message_idx}", type="primary"):
        if not class_name:
            st.error("Please enter a class name")
            return
            
        if class_name in get_existing_classes(current_code):
            st.error(f"Class name '{class_name}' already exists")
            return
            
        lines = current_code.split('\n')
        new_class = f"\nclass {class_name} {{\n"
        
        # Add attributes
        for attr in attrs_list:
            if attr["name"].strip():
                new_class += f"  {attr['visibility']}{attr['name']}"
                if attr["type"].strip():
                    new_class += f": {attr['type']}"
                new_class += "\n"
        
        # Add methods
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
        st.success(f"Class '{class_name}' has been added")
        st.rerun()

def render_modify_class(code_key, message_idx, current_code):
    """Render modify class interface"""
    existing_classes = get_existing_classes(current_code)
    if not existing_classes:
        st.info("No classes available to modify")
        return
        
    class_to_modify = st.selectbox(
        "Select Class to Modify",
        options=existing_classes,
        key=f"modify_class_{message_idx}"
    )
    
    # When the selected class changes, reset session state
    if f"last_modified_class_{message_idx}" not in st.session_state:
        st.session_state[f"last_modified_class_{message_idx}"] = class_to_modify
    elif st.session_state[f"last_modified_class_{message_idx}"] != class_to_modify:
        # Clear previous attribute and method lists
        if f"modify_attrs_list_{message_idx}" in st.session_state:
            del st.session_state[f"modify_attrs_list_{message_idx}"]
        if f"modify_methods_list_{message_idx}" in st.session_state:
            del st.session_state[f"modify_methods_list_{message_idx}"]
        st.session_state[f"last_modified_class_{message_idx}"] = class_to_modify
    
    # Parse current class information
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
    
    # Separate attributes and methods
    attributes = []
    methods = []
    for item in class_content:
        if '(' in item:  # Method
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
        else:  # Attribute
            vis = item[0] if item[0] in ['+', '-', '#'] else '+'
            try:
                name = item[1:item.index(': ')] if ': ' in item else item[1:]
                type_ = item[item.index(': ')+2:] if ': ' in item else ""
            except:
                # Handle special cases
                name = item[1:] if item else ""
                type_ = ""
            attributes.append({
                "visibility": vis,
                "name": name.strip(),
                "type": type_
            })
    
    # Initialize session state (only on first load)
    if f"modify_attrs_list_{message_idx}" not in st.session_state:
        st.session_state[f"modify_attrs_list_{message_idx}"] = attributes
    if f"modify_methods_list_{message_idx}" not in st.session_state:
        st.session_state[f"modify_methods_list_{message_idx}"] = methods
    
    new_class_name = st.text_input("New Class Name", value=class_to_modify, key=f"new_class_name_{message_idx}")
    
    # Attribute list
    st.subheader("Attribute List")
    attrs_list = st.session_state[f"modify_attrs_list_{message_idx}"]
    
    cols = st.columns([1, 2, 2, 1])
    with cols[0]:
        st.write("Visibility")
    with cols[1]:
        st.write("Name")
    with cols[2]:
        st.write("Type")
    
    for i, attr in enumerate(attrs_list):
        cols = st.columns([1, 2, 2, 1])
        with cols[0]:
            attrs_list[i]["visibility"] = st.selectbox(
                "Visibility",
                ["+", "-", "#"],
                key=f"modify_attr_vis_{message_idx}_{i}",
                label_visibility="collapsed",
                index=["+", "-", "#"].index(attr["visibility"])
            )
        with cols[1]:
            attrs_list[i]["name"] = st.text_input(
                "Name",
                value=attr["name"],
                key=f"modify_attr_name_{message_idx}_{i}",
                label_visibility="collapsed"
            )
        with cols[2]:
            attrs_list[i]["type"] = st.text_input(
                "Type",
                value=attr["type"],
                key=f"modify_attr_type_{message_idx}_{i}",
                label_visibility="collapsed"
            )
        # with cols[3]:
        #     if st.button("Delete", key=f"modify_del_attr_{message_idx}_{i}"):
        #         attrs_list.pop(i)
        #         st.session_state[f"modify_attrs_list_{message_idx}"] = attrs_list
        #         st.rerun()
    
    # if st.button("Add Attribute", key=f"modify_add_attr_{message_idx}"):
    #     attrs_list.append({"visibility": "+", "name": "", "type": ""})
    #     st.session_state[f"modify_attrs_list_{message_idx}"] = attrs_list
    #     st.rerun()
    
    # Method list
    st.subheader("Method List")
    methods_list = st.session_state[f"modify_methods_list_{message_idx}"]
    
    cols = st.columns([1, 2, 1, 2, 1])
    with cols[0]:
        st.write("Visibility")
    with cols[1]:
        st.write("Method Name")
    with cols[2]:
        st.write("Return Type")
    with cols[3]:
        st.write("Parameters")
    
    for i, method in enumerate(methods_list):
        cols = st.columns([1, 2, 1, 2, 1])
        with cols[0]:
            methods_list[i]["visibility"] = st.selectbox(
                "Visibility",
                ["+", "-", "#"],
                key=f"modify_method_vis_{message_idx}_{i}",
                label_visibility="collapsed",
                index=["+", "-", "#"].index(method["visibility"])
            )
        with cols[1]:
            methods_list[i]["name"] = st.text_input(
                "Method Name",
                value=method["name"],
                key=f"modify_method_name_{message_idx}_{i}",
                label_visibility="collapsed"
            )
        with cols[2]:
            methods_list[i]["return_type"] = st.text_input(
                "Return Type",
                value=method["return_type"],
                key=f"modify_method_return_{message_idx}_{i}",
                label_visibility="collapsed"
            )
        with cols[3]:
            methods_list[i]["params"] = st.text_input(
                "Parameters",
                value=method["params"],
                key=f"modify_method_params_{message_idx}_{i}",
                label_visibility="collapsed",
                help="Format: param1: Type1, param2: Type2"
            )
        # with cols[4]:
        #     if st.button("Delete", key=f"modify_del_method_{message_idx}_{i}"):
        #         methods_list.pop(i)
        #         st.session_state[f"modify_methods_list_{message_idx}"] = methods_list
        #         st.rerun()
    
    # if st.button("Add Method", key=f"modify_add_method_{message_idx}"):
    #     methods_list.append({"visibility": "+", "name": "", "return_type": "", "params": ""})
    #     st.session_state[f"modify_methods_list_{message_idx}"] = methods_list
    #     st.rerun()
    
    if st.button("Save Changes", key=f"save_modify_{message_idx}", type="primary"):
        # Check if new class name already exists
        if new_class_name != class_to_modify and new_class_name in get_existing_classes(current_code):
            st.error(f"Class name '{new_class_name}' already exists")
            return

        # Delete original class definition
        new_lines = []
        skip_class = False
        relationships = []  # Store all relationships
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip original class definition
            if line_stripped.startswith(f'class {class_to_modify}'):
                skip_class = True
                continue
            if skip_class and line_stripped == '}':
                skip_class = False
                continue
            
            # Collect and temporarily skip related relationships
            if any(rel in line_stripped for rel in ['<|--', '--|>', '--', '--*', '*--', '--o', 'o--']):
                # Check if it contains the class name to be modified
                if class_to_modify in line_stripped:
                    relationships.append(line)
                    continue
            
            if not skip_class:
                new_lines.append(line)
        
        # Add modified class
        insert_pos = next((i for i, line in enumerate(new_lines) 
            if '@enduml' in line.lower()), len(new_lines))
        
        # Add modified class definition
        new_class = f"\nclass {new_class_name} {{\n"
        
        # Add attributes
        for attr in attrs_list:
            if attr["name"].strip():
                new_class += f"  {attr['visibility']}{attr['name']}"
                if attr["type"].strip():
                    new_class += f": {attr['type']}"
                new_class += "\n"
        
        # Add methods
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
        
        # Insert modified class
        new_lines.insert(insert_pos, new_class)
        
        # Update and add relationships
        for relationship in relationships:
            updated_relationship = relationship
            
            # Handle quoted and unquoted cases
            if f'"{class_to_modify}"' in updated_relationship:
                updated_relationship = updated_relationship.replace(f'"{class_to_modify}"', f'"{new_class_name}"')
            else:
                # Handle various relationship patterns
                patterns = [
                    (f'{class_to_modify} ', f'{new_class_name} '),
                    (f' {class_to_modify} ', f' {new_class_name} '),
                    (f' {class_to_modify}"', f' {new_class_name}"'),
                    (f'"{class_to_modify} ', f'"{new_class_name} '),
                    (f' {class_to_modify}:', f' {new_class_name}:'),
                    (f'({class_to_modify})', f'({new_class_name})'),
                    (f' {class_to_modify}$', f' {new_class_name}'),
                ]
                for old, new in patterns:
                    updated_relationship = updated_relationship.replace(old, new)
            
            new_lines.insert(insert_pos, updated_relationship)
        
        st.session_state[code_key] = '\n'.join(new_lines)
        
        # Clear modification state
        if f"modify_attrs_list_{message_idx}" in st.session_state:
            del st.session_state[f"modify_attrs_list_{message_idx}"]
        if f"modify_methods_list_{message_idx}" in st.session_state:
            del st.session_state[f"modify_methods_list_{message_idx}"]
        
        st.success(f"Class '{class_to_modify}' has been modified to '{new_class_name}'")
        st.rerun()

def render_delete_class(code_key, message_idx, current_code):
    """Render delete class interface"""
    existing_classes = get_existing_classes(current_code)
    if existing_classes:
        class_to_delete = st.selectbox(
            "Select Class to Delete",
            options=existing_classes,
            key=f"delete_class_{message_idx}"
        )
        
        if st.button("Delete Class", key=f"delete_class_btn_{message_idx}", type="primary"):
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
                st.success(f"Class '{class_to_delete}' and its relationships have been deleted")
                st.rerun()
            else:
                st.error(f"Class '{class_to_delete}' not found")
    else:
        st.info("No classes available to delete")

def render_add_relationship(code_key, message_idx, current_code):
    """Render add relationship interface"""
    name_map = get_name_mapping(current_code)
    existing_classes = get_existing_classes(current_code)
    
    if existing_classes:
        source = st.selectbox(
            "Source Class",
            options=existing_classes,
            key=f"source_{message_idx}"
        )
        
        relation = st.selectbox(
            "Relationship Type", 
            [
                ("--", "Association"),
                ("--|>", "Inheritance"),
                ("--*", "Composition"),
                ("--o", "Aggregation"),
                ("<|--", "Reverse Inheritance"),
                ("*--", "Reverse Composition"),
                ("o--", "Reverse Aggregation")
            ],
            format_func=lambda x: f"{x[0]} ({x[1]})",
            key=f"relation_{message_idx}"
        )
        
        target = st.selectbox(
            "Target Class",
            options=existing_classes,
            key=f"target_{message_idx}"
        )
        
        source_multiplicity = st.text_input("Source Multiplicity (Optional, e.g.: 1, 0..*, 1..*)", key=f"source_mult_{message_idx}")
        target_multiplicity = st.text_input("Target Multiplicity (Optional, e.g.: 1, 0..*, 1..*)", key=f"target_mult_{message_idx}")
        
        label = st.text_input("Relationship Label (Optional)", key=f"label_{message_idx}")
        
        if st.button("Add Relationship", key=f"add_relation_{message_idx}", type="primary"):
            lines = current_code.split('\n')
            
            # Get source and target aliases (if any)
            source_alias = next((alias for alias, name in name_map.items() if name == source), source)
            target_alias = next((alias for alias, name in name_map.items() if name == target), target)
            
            # Build relationship string
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
            
            # Find all class definition start and end positions
            class_positions = []  # Store start and end positions of each class
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
            
            # Find the first independent attribute or method definition position (outside class definitions)
            method_start_pos = len(lines)
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                # Ensure not inside any class definition
                if not any(start <= i <= end for start, end in class_positions):
                    if (line_stripped.startswith('+') or 
                        line_stripped.startswith('-') or 
                        line_stripped.startswith('#')) or \
                       ('(' in line_stripped and ')' in line_stripped):
                        method_start_pos = i
                        break
            
            # Choose appropriate insertion position: after the last class definition, but before the first independent method/attribute
            if class_positions:
                last_class_end = max(pos[1] for pos in class_positions)
                insert_pos = min(last_class_end + 1, method_start_pos)
                
                # Ensure insertion position not inside any class
                while any(start <= insert_pos <= end for start, end in class_positions):
                    insert_pos = max(pos[1] + 1 for pos in class_positions if pos[1] >= insert_pos)
            else:
                insert_pos = next(i for i, line in enumerate(lines) 
                    if '@enduml' in line.lower())
            
            lines.insert(insert_pos, relation_str)
            st.session_state[code_key] = '\n'.join(lines)
            st.success("Relationship has been added")
            st.rerun()
    else:
        st.info("Please add at least one class first")

def render_delete_relationship(code_key, message_idx, current_code):
    """Render delete relationship interface"""
    existing_classes = get_existing_classes(current_code)
    if existing_classes:
        relations = []
        lines = current_code.split('\n')
        for line in lines:
            line_stripped = line.strip()
            # Check if it contains class name and relationship symbols
            has_class = any(f'"{c}"' in line_stripped or f' {c} ' in line_stripped 
                          or line_stripped.startswith(f'{c} ')
                          or line_stripped.endswith(f' {c}')
                          for c in existing_classes)
            
            # Check if it contains relationship symbols
            has_relation = any(rel in line_stripped for rel in [
                '--', '--|>', '<|--', '--*', '*--', '--o', 'o--'
            ])
            
            if has_class and has_relation:
                # Remove extra spaces and standardize spaces
                normalized_line = ' '.join(line_stripped.split())
                if normalized_line not in relations:  # Avoid duplicates
                    relations.append(normalized_line)
        
        if relations:
            relation_to_delete = st.selectbox(
                "Select Relationship to Delete",
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
            
            if st.button("Delete Relationship", key=f"delete_relation_btn_{message_idx}", type="primary"):
                # Standardize relationship to delete
                normalized_to_delete = ' '.join(relation_to_delete.split())
                # Keep lines that don't match
                new_lines = [line for line in lines 
                           if ' '.join(line.strip().split()) != normalized_to_delete]
                
                st.session_state[code_key] = '\n'.join(new_lines)
                st.success("Relationship has been deleted")
                st.rerun()
        else:
            st.info("No relationships available to delete")
    else:
        st.info("Please add at least one class first")