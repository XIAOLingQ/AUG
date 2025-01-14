<img src="./assets/框架图_页面_3.jpg">

## Abstract

Requirements modeling is essential in software development, yet manual UML modeling is time-consuming and error-prone. While large language models have been explolyed for UML modeling, their approaches remain indirect and constrained. This tool demo introduces AUG (Automated UML Model Generation), a tool for UML model generation based on the GLM4-9B model. AUG features clarification dialogues, automated requirements modeling, and online editing. The evalution show that AUG generates UML diagrams with high accuracy, achieving precision, recall, and F1 scores of 78.68\%, 67.37\%, and 72.59\%, respectively. Compared to ChatGPT 4o, AUG demonstrates improved recall and F1 scores. A questionnaire study highlights AUG’s usability and time efficiency,  with reported high satisfaction from users. The project repository including code and datasets has been available at https://github.com/XIAOLingQ/AUG, with pretraining details at https://huggingface.co/afedf/AUG

## Tool Features

<video src="https://private-user-images.githubusercontent.com/143795037/377506500-a2f4c5bb-cb06-439d-b839-29cbdd72e88d.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MjkxNzUyNTAsIm5iZiI6MTcyOTE3NDk1MCwicGF0aCI6Ii8xNDM3OTUwMzcvMzc3NTA2NTAwLWEyZjRjNWJiLWNiMDYtNDM5ZC1iODM5LTI5Y2JkZDcyZTg4ZC5tcDQ_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjQxMDE3JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI0MTAxN1QxNDIyMzBaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1iNDQ5MTlhMDgzOGE4MmQ3ZGNkZjVhMDIzNmM4MjVmOTUyNzQyYWZhNzA1OWI0ODExMWQxMmYyOTVkMTBjOWE1JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.E3cOSN_w0QwRyAh_eNfK0GhTKrNbqpJRv9uU5GcQ_Oc" data-canonical-src="https://private-user-images.githubusercontent.com/143795037/377506500-a2f4c5bb-cb06-439d-b839-29cbdd72e88d.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MjkxNzUyNTAsIm5iZiI6MTcyOTE3NDk1MCwicGF0aCI6Ii8xNDM3OTUwMzcvMzc3NTA2NTAwLWEyZjRjNWJiLWNiMDYtNDM5ZC1iODM5LTI5Y2JkZDcyZTg4ZC5tcDQ_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjQxMDE3JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI0MTAxN1QxNDIyMzBaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1iNDQ5MTlhMDgzOGE4MmQ3ZGNkZjVhMDIzNmM4MjVmOTUyNzQyYWZhNzA1OWI0ODExMWQxMmYyOTVkMTBjOWE1JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.E3cOSN_w0QwRyAh_eNfK0GhTKrNbqpJRv9uU5GcQ_Oc" controls="controls" muted="muted" class="d-block rounded-bottom-2 border-top width-fit" style="max-height:640px; min-height: 200px"></video>

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

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=XIAOLingQ/AUG&type=Date)](https://star-history.com/#XIAOLingQ/AUG&Date)
