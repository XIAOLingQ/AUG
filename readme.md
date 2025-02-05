<img src="./assets/框架图_页面_3.jpg">

## Abstract

Requirements modeling is crucial in software development, yet manual UML modeling is time-intensive and prone to errors. While Large Language Models have been used for UML modeling, their methods still indirectly rely on PlantUML parsing and are limited by the model's foundational capabilities. This demo introduces AUG (Automated UML Model Generation), a tool for generating UML class diagrams, use case diagrams, and sequence diagrams based on the GLM4-9B model. AUG features clarification dialogues, automated model building, online UML diagram editing, and quality feedback. Evaluations show AUG generates UML diagrams with high accuracy, achieving precision, recall, and F1 scores of 78.68\%, 67.37\%, and 72.59\%, respectively. Compared to ChatGPT 4o, AUG shows improved recall and F1 scores. A questionnaire study highlights AUG's usability and time efficiency, with high user satisfaction reported. The repository includes code, datasets, and evaluation data at https://github.com/XIAOLingQ/AUG, pretraining details at https://huggingface.co/afedf/AUG, and a demo video at https://youtu.be/kHbCPK6kOag.

## Tool Features

<video src="https://private-user-images.githubusercontent.com/143795037/402926288-cddabfdf-611b-4ecf-8c8c-704f605299a4.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MzY4NTU2NzQsIm5iZiI6MTczNjg1NTM3NCwicGF0aCI6Ii8xNDM3OTUwMzcvNDAyOTI2Mjg4LWNkZGFiZmRmLTYxMWItNGVjZi04YzhjLTcwNGY2MDUyOTlhNC5tcDQ_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwMTE0JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDExNFQxMTQ5MzRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT05NDk4YTViNzI0ZGViYjQ1NDdmY2QzNjA0YjA5ZDc4NmNlYmU0MjVkMzhlYzM2YTZkZDIwMzhkMmM1MzY5YjA3JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.CqGbQ2jn44J8bmdLJdPgHW8z2410ksD6e4mhSnM66vw" controls="controls" muted="muted" class="d-block rounded-bottom-2 border-top width-fit" style="max-height:640px; min-height: 200px"></video>

## Quick use

### Model deployment

You can download our pre-training weights from our huggingface repository.

```1
cd llm_serve
pip install -r requirements.txt
python api.py
```

Modify the model path from line 23 of the python file

### PlantUML server deployment

```puml
cd puml_serve
java -jar plantuml.jar -picoweb:8888 
```

### Web deployment

```client
cd web_demo/stream
pip install -r requirements.txt
streamlit run dmeo.py
```

To modify the URL for requesting LLM, update line 18 in `demo.py`.

```vue.config.js
llm_serve_url = "http://36.50.226.35:17169"
```

To modify the URL for requesting the PlantUML server, update line 7 in `./web_demo/stream/utils/uml.py`.

```
# 初始化 PlantUML
plantuml = PlantUML(url='http://www.plantuml.com/plantuml/png/')
```

## About Us

<table>
  <tr>
    <td style="width: 30%;">
      <img src="./assets/about/lj.png">
    </td>
    <td style="vertical-align: middle; padding-left: 10px;">
      Wuhan Textile University Jia Lu<br>
      Email: <a href="mailto:18713290623@163.com">18713290623@163.com</a>
    </td>
  </tr>
</table>
<table>
  <tr>
    <td style="width: 30%;">
      <img src="./assets/about/spl.png">
    </td>
    <td style="vertical-align: middle; padding-left: 10px;">
      Wuhan Textile University Peiling Sun<br>
      Email: <a href="mailto:15347274546@163.com">15347274546@163.com</a>
    </td>
  </tr>
</table>
<table>
  <tr>
    <td style="width: 30%;">
      <img src="./assets/about/lsy.png">
    </td>
    <td style="vertical-align: middle; padding-left: 10px;">
      Wuhan Textile University Shiyu Zhu<br>
      Email: <a href="mailto:1303334710@qq.com">1303334710@qq.com</a>
    </td>
  </tr>
</table>
<table>
  <tr>
    <td style="width: 30%;">
      <img src="./assets/about/zsy.png">
    </td>
    <td style="vertical-align: middle; padding-left: 10px;">
      Wuhan University Peng Liang<br>
      Email: <a href="mailto:liangp@whu.edu.cn">liangp@whu.edu.cn</a>
    </td>
  </tr>
</table>
<table>
  <tr>
    <td style="width: 30%;">
      <img src="./assets/about/zsy.png">
    </td>
    <td style="vertical-align: middle; padding-left: 10px;">
      Wuhan Textile University Yingkai Yuan<br>
      Email: <a href="mailto:15623088651@163.com">15623088651@163.com</a>
    </td>
  </tr>
</table>
<table>
  <tr>
    <td style="width: 30%;">
      <img src="./assets/about/zsy.png">
    </td>
    <td style="vertical-align: middle; padding-left: 10px;">
      Wuhan Textile University Xuanxuan Liang<br>
      Email: <a href="mailto:lxx2047734741@outlook.com">lxx2047734741@outlook.com</a>
    </td>
  </tr>
</table>
<table>
  <tr>
    <td style="width: 30%;">
      <img src="./assets/about/zsy.png">
    </td>
    <td style="vertical-align: middle; padding-left: 10px;">
      Wuhan Textile University Yimiao Zhang<br>
      Email: <a href="mailto:15632891936@163.com">15632891936@163.com</a>
    </td>
  </tr>
</table>
<table>
  <tr>
    <td style="width: 30%;">
      <img src="./assets/about/zsy.png">
    </td>
    <td style="vertical-align: middle; padding-left: 10px;">
      Wuhan Textile University Bangchao Wang<br>
      Email: <a href="mailto:wangbc@whu.edu.cn">wangbc@whu.edu.cn</a>
    </td>
  </tr>
</table>
