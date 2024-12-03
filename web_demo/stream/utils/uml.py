import requests
import base64
from plantuml import PlantUML

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
    """从 PlantUML 代码中提取现有的参与者"""
    participants = []
    lines = code.split('\n')
    for line in lines:
        line = line.strip()
        if any(line.startswith(prefix) for prefix in ['participant ', 'actor ', 'boundary ', 'control ', 'entity ', 'database ']):
            parts = line.split(' ', 2)
            if len(parts) >= 2:
                name = parts[1].strip('"')
                participants.append((name, parts[0]))  # 返回 (名称, 类型) 元组
    return participants

# 初始化 PlantUML
plantuml = PlantUML(url='http://www.plantuml.com/plantuml/png/')

def get_uml_diagram(uml_code, format='png'):
    """生成 PlantUML 图表并返回 URL 和原始数据"""
    try:
        url = plantuml.get_url(uml_code)
        response = requests.get(url)
        if response.status_code == 200:
            return {
                'url': url,
                'data': base64.b64encode(response.content).decode('utf-8'),
                'format': format
            }
        return None
    except Exception as e:
        print(f"Error generating UML diagram: {str(e)}")
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
    
    # 分析每一行来更准确地判断图表类型
    lines = code_lower.split('\n')
    
    # 计数器用于判断特征
    sequence_features = 0
    usecase_features = 0
    class_features = 0
    
    for line in lines:
        line = line.strip()
        # 类图特征
        if 'class ' in line and '{' in line:
            class_features += 2
            
        # 时序图特征
        if any(keyword in line for keyword in ['participant ', 'actor ', 'boundary ', 'control ', 'entity ', 'database ']):
            sequence_features += 1
        if 'activate ' in line or 'deactivate ' in line:
            sequence_features += 2
        if '->' in line or '<-' in line:
            sequence_features += 1
            
        # 用例图特征
        if 'usecase ' in line or '(use case)' in line:
            usecase_features += 2
        if 'actor ' in line and 'participant' not in line:  # actor在时序图中也可能出现
            usecase_features += 1
        if '<<extend>>' in line or '<<include>>' in line:
            usecase_features += 2
            
    # 根据特征计数决定图表类型
    if class_features > 0:
        return "class"
    elif sequence_features > usecase_features:
        return "sequence"
    elif usecase_features > 0:
        return "usecase"
    
    return None