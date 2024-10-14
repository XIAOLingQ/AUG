<img src="./assets/系统框架.jpeg">

我们的预训练模型地址：[afedf/AUG · Hugging Face](https://huggingface.co/afedf/AUG)

## 摘要

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
