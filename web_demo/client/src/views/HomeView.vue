<template>
  <div class="home">
    <div class="home-right">
      <div class="right-version">
        <div class="llm-chat-demo">
          <span class="chat-demo">AUG</span><span class="version"> V1</span>
        </div>
      </div>
      <div class="right-body" :class="messages.length === 0 ? 'nodata' : ''" ref="messageContainer">
        <div v-for="(message, index) in messages" class="main-message" :key="index"
          :class="{ 'user-message': message.sender === 'User', 'friend-message': message.sender === '😎' }">
          <!-- 显示用户标识和图片 -->
          <div class="message-sender"
            :class="{ 'user-message': message.sender === 'User', 'friend-message': message.sender === '😎' }">
            <img v-if="message.sender === 'User'" src="@/assets/我的.png" alt="User Icon">
            <img v-else-if="message.sender === '😎'" src="@/assets/我的2.png" alt="Friend Icon">
            <span class="message-sender-name" :class="message.sender === 'User' ? 'user-color' : 'friend-color'">{{
        message.sender }}:</span>
          </div>
          <div v-if="message.sender === 'User'" class="user-message">{{ message.content }}</div>
          <div v-else class="friend-message" v-html="message.content"></div>
        </div>
      </div>
     <div
        class="input-container"
        style="
          width: 58%;
          margin-right: 5px;
          display: flex;
          align-items: center;
          border-radius: 15px;
          background-color: #f5f5f5;
          padding: 10px;
          margin: 0 auto; /* 设置左右自动 margin 实现水平居中 */
        "
      >

        <!-- 输入框 -->
        <textarea
          v-model="queryKeyword"
          placeholder="请输入消息"
          style="
            flex-grow: 1;
            border: none;
            outline: none;
            background-color: transparent;
            padding: 5px;
          "
          rows="1"
          @input="adjustTextareaHeight"
        ></textarea>

        <!-- 发送按钮 -->
          <button
          class="send-btn"
          @click="handleSearch"
          style="
            border: none;
            background-color: black;
            color: white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            margin-left: 10px;
            cursor: pointer;
          "
        >
          <img
            v-if="!loading"
            src="@/assets/上传.png"
            alt="send"
            style="width: 20px; height: 20px"
          />
          <img
            v-else
            src="@/assets/等待.png"
            alt="loading"
            style="width: 20px; height: 20px"
          />
        </button>
      </div>
      <div class="sec-notice">AUG may also make mistakes. Please consider checking important information.</div>
    </div>
  </div>
</template>

<script>
import MarkdownIt from 'markdown-it';
import markdownItFootnote from 'markdown-it-footnote';
import markdownItTaskLists from 'markdown-it-task-lists';
import markdownItAbbr from 'markdown-it-abbr';
import markdownItContainer from 'markdown-it-container';
import hljs from 'highlight.js';
import markdownItHighlightjs from 'markdown-it-highlightjs';

export default {
  name: 'HomeView',
  components: {},
  computed: {
    // 将 Markdown 文本渲染为 HTML
    html() {
      return this.md.render(this.message);
    }
  },
  data() {
    return {
      md: new MarkdownIt()
        .use(markdownItFootnote)
        .use(markdownItTaskLists, { enabled: true })
        .use(markdownItAbbr)
        .use(markdownItContainer, 'warning')
        .use(markdownItHighlightjs, { hljs }), // 添加 markdown-it-highlightjs 插件
      queryKeyword: '',
      tempResult: {},
      loading: false,
      messages: [],
      socket: null,
      eventSource: null, // 添加事件源变量
      stopIcon: '@/assets/等待.png',
      uploadIcon: '@/assets/上传.png'
    }
  },
  methods: {
    async handleSearch() {
      // 如果正在加载中，则不执行新的搜索操作
      if (this.loading || !this.queryKeyword.trim()) {
        return; // 防止重复触发或发送空消息
      }

      const keyword = this.queryKeyword;
      this.loading = true;
      try {
        let zxakey = "zxa";
        // 初始化一个用于 SSE 的 message 对象
        let sseMessage = {
          orgcontent: '',
          content: '',
          sender: '😎',
          zxakey: zxakey
        };

        this.messages.push({
          content: keyword,
          sender: 'User'
        });

        this.$nextTick(() => {
          this.scrollToBottom();
        });

        let friendMessage = sseMessage;
        // 创建一个新的 EventSource 实例
        this.eventSource = new EventSource('llm/request?query=' + keyword);
        // 设置消息事件监听器
        this.eventSource.onmessage = (event) => {          try {
            const dataObject = JSON.parse(event.data);
            // 判断是否为最后一个消息，如果是，则关闭事件源
            if (dataObject.message === 'done') {
              this.eventSource.close();
              this.loading = false;
            }
            if (dataObject.message != 'done') {
              // 累加接收到的数据到 friendMessage.orgcontent 中
              friendMessage.orgcontent += dataObject.message.toLocaleString();
              friendMessage.orgcontent = friendMessage.orgcontent.replace(/\*\*\s*([^*]*?)\s*(:\s*)?\*\*/g, '**$1$2**');
              // 更新 friendMessage.content，这里假设 md.render 可以处理累加的字符串
              friendMessage.content = this.md.render(friendMessage.orgcontent);
            }
            this.scrollToBottom();
          } catch (e) {
            console.error('Error parsing JSON:', e);
          }
        };
        this.messages.push(sseMessage);
        this.queryKeyword = ''; // 清空输入框
        this.eventSource.onerror = error => {
          console.error('EventSource failed:', error);
          this.eventSource.close();
        };
      } catch (error) {
        console.error('发送消息时出错：', error);
         this.loading = false; // 出错时停止加载
      } finally {

      }
    },
    closeEventSource() {
      this.loading = false;
      if (this.eventSource) {
        this.eventSource.close();
      }
    },
    scrollToBottom() {
      const messageContainer = this.$refs.messageContainer;
      if (messageContainer) {
        messageContainer.scrollTop = messageContainer.scrollHeight;
      }
    },
    beforeDestroy() {
      if (this.eventSource) {
        this.eventSource.close();
      }
    },
    addCopyButtonToCodeBlocks() {
      this.$nextTick(() => {
        const codeBlocks = this.$el.querySelectorAll('.friend-message pre .hljs');
        codeBlocks.forEach(block => {
          // 创建复制按钮
          const button = document.createElement('button');
          button.classList.add('copy-button');
          button.innerText = '生成预览图';
          button.onclick = async () => {
            // 获取代码块中的 Markdown 内容
            const markdownContent = block.innerText;

            // 发送 POST 请求到指定的 URL
            try {
              const response = await fetch('get_uml', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({ markdown: markdownContent })  // 将 Markdown 内容作为请求体发送
              });

              // 处理返回的数据，在新窗口中显示预览图
              if (response.ok) {
                const data = await response.json();
                const previewUrl = data.url;  // 服务器返回的图片预览链接
                window.open(previewUrl);
              //
              //   // 打开一个新窗口并展示生成的 UML 图像
              //   const newWindow = window.open();
              //   if (newWindow) {
              //     // 设置图片大小为 80% 的宽度，高度自适应
              // //     newWindow.document.write(`
              // //   <img src="${previewUrl}" alt="预览图" style="width: 30%; height: auto; display: block; margin: 0 auto;">
              // // `);
              //     //newWindow.document.title = "UML 预览图";  // 设置新窗口的标题
              //   } else {
              //     console.error('新窗口无法打开。请检查浏览器的弹窗设置。');
              //   }
              } else {
                console.error('Failed to generate preview:', response.statusText);
              }
            } catch (error) {
              console.error('Error:', error);
            }
          };

          // 确保按钮定位在代码块右上角
          block.parentNode.style.position = 'relative';
          button.style.backgroundColor = '#f7f1fd';  // 设置按钮背景颜色
          button.style.position = 'absolute';
          button.style.top = '10px';
          button.style.right = '10px';
          block.parentNode.appendChild(button);
          button.style.border = 'none';
          button.style.borderRadius = '15px';  // 设置按钮的圆角
          button.style.marginBottom = '12px';  // 设置按钮的下边距
        });
      });
    },

    async resetMessages() {
      try {
        const response = await fetch('reset_messages', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          console.log("请求成功:", data);
        } else {
          console.error('请求失败:', response.statusText);
        }
      } catch (error) {
        console.error('请求错误:', error.message);
        console.error('更多错误信息:', error);
      }
    }

  },


  mounted() {
    this.addCopyButtonToCodeBlocks();
    this.resetMessages();

  },
  updated() {
    this.addCopyButtonToCodeBlocks();
  }

}
</script>

<style scoped>
.home {
  height: 100%;
  display: flex;
  position: relative;
  /* 需要设置为相对定位 */
  overflow: hidden;
  /* 确保背景图片不会溢出 */
}

.home::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url('../assets/photo.png');
  /* 设置背景图片路径 */
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  filter: blur(1px);
  /* 设置背景模糊效果 */
  z-index: -1;
  /* 确保背景在内容的后面 */
  opacity: 0.8;
  /* 设置背景图片的透明度（可选） */
}

.home-right {
  width: 100%;
}

.right-version {
  //width: 60%;
  margin: auto;
  //background-color: #F9FFD8;
  height: 5%;
  display: flex;
  justify-content: start;
  align-items: center;
  border-radius: 15px;
  margin-bottom: 12px;
}

.version {
  color: rgb(155, 155, 155);
}

.llm-chat-demo {
  width: 58%;
  margin: auto;
  margin-left: 20px;
  font-family: "黑体", "SimHei", sans-serif;
  font-family: Söhne, ui-sans-serif, system;
  font-variation-settings: normal;
  font-weight: 550;
  font-size: 18px;
  cursor: pointer;
  color-scheme: light;
}

.chat-demo {
  color: #000000;

}

.right-body {
  height: 85%;
  overflow-y: auto;
}

.user-color {
  color: #223a47;
}

.friend-color {
  color: #2c3d29;
}



.main-message {
  margin: auto;
  width: 58%;
  justify-content: center;
  margin-top: 1px;
  margin-bottom: 1px;
}

.message-sender-name {
  margin-left: 10px;
  font-family: "黑体", "SimHei", sans-serif;
  font-family: Söhne, ui-sans-serif, system;
  font-weight: 550;
  font-size: 18px;
  margin-top: 1px;
  margin-bottom: 1px;

}

.right-input {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 6.5%;

  position: relative;
}

.sec-notice {
  height: 3.5%;
  font-size: 12px;
  font-family: Söhne, ui-sans-serif;
  color: rgb(155, 155, 155);
  display: flex;
  justify-content: center;
}

.input {
  width: 58%;
  margin-right: 5px;
}

.up-load {
  //width: 30px;
}

::v-deep .el-button {
  padding: 5px 6px;
}

::v-deep .el-input__inner {
  height: 52px;
  border-radius: 15px;
  border: 1px solid #DCDFE6;
}

::v-deep .el-button--primary {
  position: relative;
  right: 3.5%;
  background-color: rgba(180, 180, 180) !important;
  color: black !important;
  border-color: rgba(180, 180, 180) !important;
}

.user-message {
  text-align: left;
  padding: 5px;
  margin-bottom: 5px;
  margin-top: 0;
  border-radius: 15px;
  background-color: rgb(250, 245, 236);

}

.friend-message {
  background-color: rgb(214, 243, 243);
  /* 这里的 0.5 是透明度，你可以根据需要调整 */
  text-align: left;
  padding: 5px;
  margin-bottom: 5px;
  margin-bottom: 5px;
  border-radius: 15px;
}

::v-deep .friend-message pre .hljs {
  border-radius: 10px !important;
  /* 圆角 */
  background-color: #FAF7F7;
  /* 例子中的背景色 */
}

/* 设置滚动条的样式 */
::-webkit-scrollbar {
  width: 6px;
  /* 设置滚动条宽度 */
}

/* 设置滚动条轨道的样式 */
::-webkit-scrollbar-track {
  background: #f1f1f1;
  /* 设置滚动条轨道的背景色 */
}

/* 设置滚动条滑块的样式 */
::-webkit-scrollbar-thumb {
  background: #888;
  /* 设置滚动条滑块的背景色 */
  border-radius: 3px;
  /* 设置滚动条滑块的圆角 */
}

/* 鼠标悬停时滚动条滑块的样式 */
::-webkit-scrollbar-thumb:hover {
  background: #555;
  /* 设置鼠标悬停时滚动条滑块的背景色 */
}

.copy-button {
  background-color: #4c5eaf;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 5px 10px;
  font-size: 12px;
  cursor: pointer;
}

.copy-button:hover {
  background-color: #b1abe6;
}

::v-deep .friend-message pre .hljs {
  border-radius: 10px !important;
  /* 保持圆角 */
  background-color: #3b3b3b;
  /* 保持代码块的背景色 */
  position: relative;
  /* 确保复制按钮能够绝对定位 */
  color: #ffffff;                  /* 设置文字颜色为深灰色 */
}
</style>
