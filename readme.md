# AUG - Automated UML Model Generation

<div align="center">
    <img src="./assets/框架图_页面_3.jpg" alt="AUG Framework">
    <p>
        <a href="https://github.com/XIAOLingQ/AUG/blob/main/LICENSE">
            <img alt="License" src="https://img.shields.io/github/license/XIAOLingQ/AUG.svg?color=blue">
        </a>
        <a href="https://huggingface.co/afedf/AUG">
            <img alt="Hugging Face" src="https://img.shields.io/badge/🤗%20Hugging%20Face-AUG-blue">
        </a>
        <a href="https://youtu.be/kHbCPK6kOag">
            <img alt="Demo Video" src="https://img.shields.io/badge/Demo-Video-red">
        </a>
    </p>
</div>

## 📖 Overview

AUG (Automated UML Model Generation) is an innovative tool that leverages the GLM4-9B model to automate UML diagram generation from natural language requirements. Our system achieves state-of-the-art performance in generating class diagrams, use case diagrams, and sequence diagrams.

### Key Features
- 🤖 **Intelligent Dialogue**: Interactive clarification system for requirement refinement
- 📊 **Multiple Diagram Types**: Support for class, use case, and sequence diagrams
- ✏️ **Online Editing**: Built-in UML diagram editor
- 📈 **Quality Feedback**: Automated evaluation and suggestions
- 🎯 **High Accuracy**: Superior performance metrics compared to existing solutions

### Performance Metrics
- Precision: 78.68%
- Recall: 67.37%
- F1 Score: 72.59%

*Note: Our system demonstrates improved recall and F1 scores compared to ChatGPT 4.0*

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Java Runtime Environment (for PlantUML)
- Git

### 1. Model Deployment
```bash
cd llm_serve
pip install -r requirements.txt
python api.py
```
Configure model path in `api.py` (line 23):
```python
model_path = "your/model/path"  # Set your model path here
```

### 2. PlantUML Server
```bash
cd puml_serve
java -jar plantuml.jar -picoweb:8888
```

### 3. Web Interface
```bash
cd web_demo
pip install -r requirements.txt
streamlit run demo.py
```

### Configuration
1. LLM Service URL (in `demo.py`, line 18):
```python
llm_serve_url = "http://36.50.226.35:17169"  # Update with your LLM service URL
```

2. PlantUML Server URL (in `./web_demo/stream/utils/uml.py`, line 7):
```python
plantuml = PlantUML(url='http://www.plantuml.com/plantuml/png/')  # Update with your PlantUML server URL
```

## 📺 Demo
<div align="center">
    <video src="https://private-user-images.githubusercontent.com/143795037/402926288-cddabfdf-611b-4ecf-8c8c-704f605299a4.mp4" controls="controls" muted="muted" style="max-width:800px;">
    </video>
</div>

## 📚 Resources
- [📦 Model Weights (Hugging Face)](https://huggingface.co/afedf/AUG)
- [📹 Demo Video](https://youtu.be/kHbCPK6kOag)
- [💻 Source Code](https://github.com/XIAOLingQ/AUG)

## 👥 Team

### Wuhan Textile University
- **Jia Lu** - [18713290623@163.com](mailto:18713290623@163.com)
- **Peiling Sun** - [15347274546@163.com](mailto:15347274546@163.com)
- **Shiyu Zhu** - [1303334710@qq.com](mailto:1303334710@qq.com)
- **Yingkai Yuan** - [15623088651@163.com](mailto:15623088651@163.com)
- **Xuanxuan Liang** - [lxx2047734741@outlook.com](mailto:lxx2047734741@outlook.com)
- **Yimiao Zhang** - [15632891936@163.com](mailto:15632891936@163.com)
- **Bangchao Wang** - [wangbc@whu.edu.cn](mailto:wangbc@whu.edu.cn)

### Wuhan University
- **Peng Liang** - [liangp@whu.edu.cn](mailto:liangp@whu.edu.cn)

## 📄 License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing
We welcome contributions! Please feel free to submit a Pull Request.

