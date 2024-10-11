<template>
  <div>
    <div v-html="html" class="zxa"></div>
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
  data() {
    return {
      markdown: `

** 快速排序 **算法是一种基于分治法的高效排序
以下是一个简单的快速排序算法的Python实现：

\`\`\`python
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    less = [x for x in arr[1:] if x <= pivot]
    greater = [x for x in arr[1:] if x > pivot]
    return quick_sort(less) + [pivot] + quick_sort(greater)

example_array = [7, 2, 1, 6, 8, 5, 3, 4]
sorted_array = quick_sort(example_array)
print(sorted_array)
\`\`\`

这个代码实现了快速排序算法。

`,
      md: new MarkdownIt()
        .use(markdownItFootnote)
        .use(markdownItTaskLists, { enabled: true })
        .use(markdownItAbbr)
        .use(markdownItContainer, 'warning')
        .use(markdownItHighlightjs, { hljs }), // 添加 markdown-it-highlightjs 插件
    };
  },
  computed: {
    html() {
      // 预处理 Markdown 以渲染内容
      this.markdown = this.markdown.replace(/\*\*\s*([^*]*?)\s*(:\s*)?\*\*/g, '**$1$2**');
      return this.md.render(this.markdown);
    }
  },
  mounted() {
    // 代码块渲染后添加复制按钮
    this.addCopyButtons();
  },
  methods: {
    addCopyButtons() {
      // 查找所有的 code 元素
      const codeBlocks = document.querySelectorAll('pre code');

      codeBlocks.forEach((block) => {
        const button = document.createElement('button');
        button.innerText = '复制';
        button.classList.add('copy-button');

        // 按钮点击事件
        button.addEventListener('click', () => {
          const codeText = block.innerText;
          navigator.clipboard.writeText(codeText)
              .then(() => {
                alert('代码已复制!');
              })
              .catch(err => {
                console.error('复制失败:', err);
              });
        });

        // 将按钮插入到每个代码块上方
        block.parentNode.style.position = 'relative';
        block.parentNode.appendChild(button);
      });
    }
  }
}
</script>

<style scoped>
.zxa {
  margin: auto;
  width: 600px;
}

::v-deep .zxa pre .hljs {
  border-radius: 10px !important;
  padding: 1em;
  background-color: #f5f5f5;
  position: relative; /* 确保按钮定位正确 */
}

.copy-button {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 5px 10px;
  font-size: 12px;
  cursor: pointer;
  border: none;
  border-radius: 5px;
  background-color: #007bff;
  color: white;
  transition: background-color 0.3s ease;
}

.copy-button:hover {
  background-color: #0056b3;
}
</style>
