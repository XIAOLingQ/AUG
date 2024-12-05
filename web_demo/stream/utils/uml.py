import requests
import base64
from plantuml import PlantUML
import re

def create_usecase_template():
    """创建用例图的基本模板"""
    return """@startuml
skinparam packageStyle rectangle
skinparam handwritten false
skinparam actorStyle awesome

' 在这里添加元素

@enduml
"""
def create_sequence_template():
    """创建时序图的基本模板"""
    return """@startuml
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true
skinparam maxMessageSize 200

' 在这里添加元素

@enduml
"""

def get_existing_participants(code):
    """从 PlantUML 代码中提取现有的参与者和 actor"""
    participants = []
    lines = code.split('\n')
    for line in lines:
        line = line.strip()
        # 检查所有可能的参与者类型
        if any(line.startswith(prefix) for prefix in [
            'participant ', 'actor ', 'boundary ', 
            'control ', 'entity ', 'database '
        ]):
            # 提取参与者类型
            participant_type = line.split(' ')[0]
            
            # 处理带引号的名称
            name_match = re.search(r'"([^"]+)"', line)
            if name_match:
                original_name = name_match.group(1)
                
                # 检查是否有别名
                if ' as ' in line:
                    # 别名在 as 之后
                    alias = line.split(' as ')[-1].strip()
                    participants.append((original_name, participant_type))
                else:
                    participants.append((original_name, participant_type))
            else:
                # 处理不带引号的情况
                parts = line.split(' ')
                if len(parts) >= 2:
                    name = parts[1].strip()
                    participants.append((name, participant_type))
    
    return participants

def get_name_mapping(code):
    """获取名称映射（别名到原始名称）"""
    name_map = {}
    lines = code.split('\n')
    for line in lines:
        line = line.strip()
        # 检查所有可能的参与者类型
        if any(line.startswith(prefix) for prefix in [
            'participant ', 'actor ', 'boundary ', 
            'control ', 'entity ', 'database '
        ]):
            # 提取带引号的名称
            name_match = re.search(r'"([^"]+)"', line)
            if name_match and ' as ' in line:
                original_name = name_match.group(1)
                alias = line.split(' as ')[-1].strip()
                name_map[alias] = original_name
    return name_map

# 初始化 PlantUML
plantuml = PlantUML(url='http://127.0.0.1:8888/plantuml/png/')

def get_uml_diagram(uml_code, format='png'):
    """生成 PlantUML 图表并返回 URL 和原始数据"""
    try:
        print("开始生成 UML 图...")  # 打印开始
        url = plantuml.get_url(uml_code)
        print(f"PlantUML URL: {url}")  # 打印 URL
        
        response = requests.get(url)
        print(f"HTTP 状态码: {response.status_code}")  # 打印状态码
        
        if response.status_code == 200:
            result = {
                'url': url,
                'data': base64.b64encode(response.content).decode('utf-8'),
                'format': format
            }
            print("图像生成成功")  # 打印成功
            return result
        
        print(f"请求失败: {response.text}")  # 打印失败原因
        return None
    except Exception as e:
        print(f"生成图表错误: {str(e)}")  # 打印错误
        return None

def get_existing_classes(code):
    """从 PlantUML 代码中提取现有的类名"""
    classes = []
    lines = code.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('class '):
            class_name = line.split(' ')[1].split('{')[0].split('<')[0].strip()
            classes.append(class_name)
    return classes 

def get_diagram_type(code):
    """检测 UML 图表类型"""
    code_lower = code.lower()
    if '@startuml' not in code_lower:
        return None
    
    # 类图特征
    has_class = 'class ' in code_lower and '{' in code_lower
    
    # 时序图特征
    has_participant = any(keyword in code_lower for keyword in ['participant ','boundary ', 'control ', 'entity ', 'database '])
    has_message = '->' in code_lower or '<-' in code_lower
    
    # 用例图特征
    has_usecase = 'usecase ' in code_lower or 'rectangle' in code_lower
    
    # 判断图表类型
    if has_class:
        return "class"
    elif has_participant and has_message:
        return "sequence"
    elif has_usecase:
        return "usecase"
    
    return None

def get_existing_actors(code):
    """从 PlantUML 代码中提取现有的 Actor"""
    actors = []
    lines = code.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('actor '):
            # 处理带 as 的情况
            parts = line.split(' as ')
            if len(parts) == 2:
                # 提取原始名称（���能带引号）
                first_part = parts[0].split(' ', 1)
                if len(first_part) >= 2:
                    actor_name = first_part[1].strip('"')
                    actors.append(actor_name)
            else:
                # 处理不带 as 的情况
                parts = line.split(' ', 2)
                if len(parts) >= 2:
                    actor_name = parts[1].strip('"')
                    actors.append(actor_name)
    return actors

def get_existing_usecases(code):
    """从 PlantUML 代码中提取现有的用例"""
    usecases = []
    lines = code.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('usecase '):
            # 处理带 as 的情况
            parts = line.split(' as ')
            if len(parts) == 2:
                # 提取原始名称（可能带引号）
                first_part = parts[0].split(' ', 1)
                if len(first_part) >= 2:
                    usecase_name = first_part[1].strip('"')
                    usecases.append(usecase_name)
            else:
                # 处理不带 as 的情况
                match = re.search(r'usecase\s*"([^"]+)"', line)
                if match:
                    usecase_name = match.group(1)
                    usecases.append(usecase_name)
    return usecases