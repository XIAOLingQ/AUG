<img src="./assets/框架图_页面_3.jpg">

## 摘要

Requirements modeling is essential in software development, yet manual UML modeling is time-consuming and error-prone. While large language models have been explolyed for UML modeling, their approaches remain indirect and constrained. This tool demo introduces AUG (Automated UML Model Generation), a tool for UML model generation based on the GLM4-9B model. AUG features clarification dialogues, automated requirements modeling, and online editing. The evalution show that AUG generates UML diagrams with high accuracy, achieving precision, recall, and F1 scores of 78.68\%, 67.37\%, and 72.59\%, respectively. Compared to ChatGPT 4o, AUG demonstrates improved recall and F1 scores. A questionnaire study highlights AUG’s usability and time efficiency,  with reported high satisfaction from users. The project repository including code and datasets has been available at https://github.com/XIAOLingQ/AUG, with pretraining details at https://huggingface.co/afedf/AUG

## 工具功能

<video src="https://private-user-images.githubusercontent.com/143795037/377506500-a2f4c5bb-cb06-439d-b839-29cbdd72e88d.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MjkxNzUyNTAsIm5iZiI6MTcyOTE3NDk1MCwicGF0aCI6Ii8xNDM3OTUwMzcvMzc3NTA2NTAwLWEyZjRjNWJiLWNiMDYtNDM5ZC1iODM5LTI5Y2JkZDcyZTg4ZC5tcDQ_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjQxMDE3JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI0MTAxN1QxNDIyMzBaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1iNDQ5MTlhMDgzOGE4MmQ3ZGNkZjVhMDIzNmM4MjVmOTUyNzQyYWZhNzA1OWI0ODExMWQxMmYyOTVkMTBjOWE1JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.E3cOSN_w0QwRyAh_eNfK0GhTKrNbqpJRv9uU5GcQ_Oc" data-canonical-src="https://private-user-images.githubusercontent.com/143795037/377506500-a2f4c5bb-cb06-439d-b839-29cbdd72e88d.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MjkxNzUyNTAsIm5iZiI6MTcyOTE3NDk1MCwicGF0aCI6Ii8xNDM3OTUwMzcvMzc3NTA2NTAwLWEyZjRjNWJiLWNiMDYtNDM5ZC1iODM5LTI5Y2JkZDcyZTg4ZC5tcDQ_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjQxMDE3JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI0MTAxN1QxNDIyMzBaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1iNDQ5MTlhMDgzOGE4MmQ3ZGNkZjVhMDIzNmM4MjVmOTUyNzQyYWZhNzA1OWI0ODExMWQxMmYyOTVkMTBjOWE1JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.E3cOSN_w0QwRyAh_eNfK0GhTKrNbqpJRv9uU5GcQ_Oc" controls="controls" muted="muted" class="d-block rounded-bottom-2 border-top width-fit" style="max-height:640px; min-height: 200px"></video>

## 使用方法

### 模型部署

可以从我们的huggingface仓库中下载我们的预训练权重模型将他们放入./models文件夹中，我们提供了API部署方式的代码以符合我们项目的需要；如果需要终端交互可以使用官网提供的方法。

```1
cd llm_serve
pip install -r requirements.txt
python api.py
```

### PlantUML服务器部署

```puml
cd puml_serve
java -jar plantuml.jar -picoweb:8888  //更换运行的端口
```

### web部署

我们的前端使用Vue，后端使用Flask快速开发。

#### 前端

```client
cd web_demo/client
npm install
npm run serve
```

如果要修改请求后端的url，修改文件./web_demo/client/vue.config.js 的第六行

```vue.config.js
target: 'http://27.25.158.240:21561', // 你的后端接口地址
//替换为你的后端地址
```

#### 后端

```serve
cd web_demo/server
pip install -r requirements.txt
python app.py
```

如果要修改请求大模型的地址或请求plantUML服务器的地址，修改文件app.py的第17行和第18行。

## 关于我们

<table>
  <tr>
    <td style="width: 30%;">
      <img src="./assets/about/lj.png">
    </td>
    <td style="vertical-align: middle; padding-left: 10px;">
      武汉纺织大学 卢佳<br>
      Email: <a href="mailto:2204240222@mail.wtu.edu.cn">2204240222@mail.wtu.edu.cn</a>
    </td>
  </tr>
</table>
<table>
  <tr>
    <td style="width: 30%;">
      <img src="./assets/about/spl.png">
    </td>
    <td style="vertical-align: middle; padding-left: 10px;">
      武汉纺织大学 孙培伶<br>
      Email: <a href="mailto:2204240513@mail.wtu.edu.cn">2204240513@mail.wtu.edu.cn</a>
    </td>
  </tr>
</table>
<table>
  <tr>
    <td style="width: 30%;">
      <img src="./assets/about/lsy.png">
    </td>
    <td style="vertical-align: middle; padding-left: 10px;">
      武汉纺织大学 李思雨<br>
      Email: <a href="mailto:2204240106@mail.wtu.edu.cn">2204240106@mail.wtu.edu.cn</a>
    </td>
  </tr>
</table>
<table>
  <tr>
    <td style="width: 30%;">
      <img src="./assets/about/zsy.png">
    </td>
    <td style="vertical-align: middle; padding-left: 10px;">
      武汉纺织大学 朱诗雨<br>
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
      武汉纺织大学 袁瑛凯<br>
      Email: <a href="mailto:3403613474@qq.com">3403613474@qq.com</a>
    </td>
  </tr>
</table>
<table>
  <tr>
    <td style="width: 30%;">
      <img src="./assets/about/zsy.png">
    </td>
    <td style="vertical-align: middle; padding-left: 10px;">
      武汉纺织大学 陈億<br>
      Email: <a href="mailto:3458981693@qq.com">3458981693@qq.com</a>
    </td>
  </tr>
</table>

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=XIAOLingQ/AUG&type=Date)](https://star-history.com/#XIAOLingQ/AUG&Date)
