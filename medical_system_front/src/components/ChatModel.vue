<template>
  <!-- 根容器：水平布局，设置高度、外边距、背景、圆角、阴影、溢出处理和边框 -->
  <div class="flex h-[90vh] mt-10 bg-gray-100 rounded-2xl shadow-xl overflow-hidden border border-gray-200">
    <!-- 左侧边栏容器：用于会话列表，垂直布局，白色背景，右侧边框，固定宽度并带过渡动画 -->
    <div
      class="flex flex-col bg-white border-r border-gray-200 w-72 transition-all duration-300"
    >
      <!-- 顶部按钮区：垂直布局、左对齐、间距、内边距，下边框和灰色背景 -->
      <div class="flex flex-col items-start space-y-3 p-4 border-b bg-gray-50">
        <!-- 标题：会话列表 -->
        <h2 class="text-lg font-semibold text-gray-800">💬 会话列表</h2>

        <!-- 历史会话按钮：点击触发 loadSessions 方法 -->
        <button
          @click="loadSessions"
          class="w-full text-sm bg-gray-300 text-gray-800 px-3 py-2 rounded-lg hover:bg-gray-400 transition text-left"
        >
          📂 历史会话
        </button>

        <!-- 新对话按钮：点击触发 newChat 方法，带渐变背景 -->
        <button
          @click="newChat"
          class="w-full text-sm bg-gradient-to-r from-purple-500 to-indigo-500 text-white px-3 py-2 rounded-lg hover:opacity-90 transition text-left"
        >
          ✨ 新对话
        </button>

        <!-- 展开/收起列表按钮：点击触发 toggleList，显示状态由 showList 控制 -->
        <button
          @click="toggleList"
          class="w-full text-sm bg-gray-200 text-gray-800 px-3 py-2 rounded-lg hover:bg-gray-300 transition text-left"
        >
          {{ showList ? '⬅️ 收起' : '➡️ 展开' }}
        </button>
      </div>

      <!-- 历史会话列表区域：根据 showList 控制显示，支持滚动 -->
      <div
        v-show="showList"
        class="flex-1 p-2 space-y-2 overflow-auto transition-all duration-300"
      >
        <!-- 遍历 sessions 渲染会话项 -->
        <div
          v-for="session in sessions"
          :key="session.id"
          class="flex items-center justify-between group"
        >
          <!-- 会话项：点击触发 selectSession，显示标题，当前会话样式不同 -->
          <div
            @click="selectSession(session.id)"
            class="flex-1 p-3 rounded-lg cursor-pointer text-sm font-medium transition-all truncate"
            :class="session.id === currentSessionId
              ? 'bg-blue-500 text-white shadow-md'
              : 'hover:bg-gray-100 text-gray-700'">
            <!-- 会话标题，若无标题显示“未命名对话” -->
            <div class="font-semibold truncate">{{ session.title || '未命名对话' }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧主聊天界面：垂直布局、占满剩余空间、内边距和背景 -->
    <div class="flex flex-col flex-1 p-6 bg-gray-50 transition-all duration-300">
      <!-- 顶部区域：页面标题和当前会话显示 -->
      <div class="flex justify-between items-center mb-4">
        <!-- 页面主标题 -->
        <h1 class="text-2xl font-semibold text-gray-800">🤖 大模型交互界面</h1>
        <!-- 显示当前会话标题或“新会话” -->
        <div class="text-gray-500 text-sm">
          当前会话：{{ currentSession?.title || '新会话' }}
        </div>
      </div>

      <!-- 上传 PDF 模块：文件输入隐藏，通过按钮触发选择 -->
      <div class="flex items-center space-x-3 mb-4">
        <!-- 隐藏的文件输入框，仅接受 PDF，change 事件触发 handlePdfUpload -->
        <input type="file" id="pdfInput" accept="application/pdf" class="hidden" @change="handlePdfUpload" />
        <!-- 触发文件选择的按钮 -->
        <button
          @click="triggerFileSelect"
          class="bg-green-500 text-white px-4 py-2 rounded-xl text-sm font-semibold hover:bg-green-600 transition">
          📄 上传 PDF
        </button>

        <!-- 在聊天记录区域下方添加知识库查询按钮 -->
        <div class="flex items-center justify-end mb-0">
          <button
            @click="toggleKnowledgeMode"
            :disabled="ragLoading"
            :class="[
              'px-4 py-2 rounded-2xl font-semibold shadow-md transition text-sm ml-2',
              isKnowledgeMode
                ? (ragLoading ? 'bg-green-300 text-white cursor-not-allowed' : 'bg-green-500 text-white hover:bg-green-600')
                : (ragLoading ? 'bg-orange-300 text-white cursor-not-allowed' : 'bg-orange-500 text-white hover:bg-orange-600')
            ]"
          >
            {{ ragLoading ? (isKnowledgeMode ? '⏳ 知识检索中...' : '⏳ 查询中...') : (isKnowledgeMode ? '🧠 知识库模式' : '📚 知识库查询') }}
          </button>
        </div>

        <!-- 上传状态提示：上传中、成功或错误 -->
        <span v-if="uploading" class="text-gray-500 text-sm">⏳ 正在上传中...</span>
        <span v-if="uploadSuccess" class="text-green-600 text-sm">✅ 上传成功！</span>
        <span v-if="uploadError" class="text-red-500 text-sm">❌ {{ uploadError }}</span>
      </div>

      <!-- Milvus 处理模块：输入集合名、db_path 并触发处理 -->
      <div class="flex items-center space-x-3 mb-4">
        <!-- Milvus 集合名输入框，双向绑定 collectionName -->
        <input
          type="text"
          v-model="collectionName"
          placeholder="输入 Milvus 集合名"
          class="flex-1 p-2 border border-gray-300 rounded-xl text-sm"
        />
        <!-- Milvus db_path 输入框，双向绑定 dbPath -->
        <input
          type="text"
          v-model="dbPath"
          placeholder="输入 Milvus db_path"
          class="flex-1 p-2 border border-gray-300 rounded-xl text-sm"
        />
        <!-- 触发 PDF 转向量并入 Milvus 的按钮，disabled 状态由 processing 控制 -->
        <button
          @click="processPdfs"
          :disabled="processing"
          class="px-4 py-2 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition disabled:opacity-60 disabled:cursor-not-allowed text-sm"
        >
          {{ processing ? '处理中...' : '📄 PDF 转向量入 Milvus' }}
        </button>
      </div>

      <!-- 处理成功或错误提示 -->
      <div v-if="processSuccess" class="text-green-600 text-sm mb-2">✅ 处理完成！</div>
      <div v-if="processError" class="text-red-500 text-sm mb-2">{{ processError }}</div>

      <!-- 已上传 PDF 文件列表区域，只有当 pdfList 有项时显示 -->
      <div v-if="pdfList.length" class="mb-6 bg-white rounded-2xl shadow-inner p-3 border border-gray-200">
        <!-- 区块标题 -->
        <h3 class="text-sm font-semibold text-gray-700 mb-2">📚 已上传 PDF 文件</h3>
        <!-- 列表 -->
        <ul class="space-y-1 text-sm">
          <!-- 遍历 pdfList 渲染每个文件项 -->
          <li
            v-for="pdf in pdfList"
            :key="pdf.id"
            class="flex justify-between items-center border-b border-gray-100 py-1">
            <!-- 文件名，超出截断 -->
            <span class="truncate">{{ pdf.filename }}</span>
            <!-- 下载链接，使用后端提供的下载接口 -->
            <a
              :href="`${API_BASE}/download_pdf/${pdf.id}`"
              class="text-blue-500 hover:underline"
              target="_blank">
              下载
            </a>
          </li>
        </ul>
      </div>

      <!-- 聊天 记录区域：可滚动，背景白色，圆角，内阴影 -->
      <div
        ref="chatContainer"
        class="flex-1 overflow-y-auto mb-4 p-4 bg-white rounded-2xl shadow-inner chat-container relative"
      >
        <!-- 当当前会话没有消息时显示占位提示 -->
        <div v-if="!currentSession?.messages?.length" class="text-center text-gray-400 mt-20">
          💬 还没有开始聊天，试着输入点什么吧~
        </div>

        <!-- 遍历当前会话的消息列表，渲染消息气泡 -->
        <div
          v-for="(msg, index) in currentSession?.messages || []"
          :key="index"
          class="flex mb-4 flex-col"
          :class="msg.role === 'user' ? 'items-end' : 'items-start'"
        >
          <!-- 每条消息的头部区域：头像 + 气泡 -->
          <div class="flex items-center mb-1">
            <!-- 助手头像（左侧） -->
            <div v-if="msg.role === 'assistant'" class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3 text-blue-500 font-bold">
              🤖
            </div>
            <!-- 用户头像（右侧） -->
            <div v-if="msg.role === 'user'" class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center ml-3 text-green-500 font-bold order-2">
              🧑
            </div>

            <!-- 消息气泡：根据角色切换样式（用户蓝色渐变，助手灰色） -->
            <div
              :class="[
                'max-w-[70%] px-4 py-3 rounded-2xl text-sm shadow-md break-words transition-all duration-200',
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-br-none'
                  : 'bg-gray-200 text-gray-800 rounded-bl-none'
              ]"
            >
              <!-- 显示消息内容 -->
              <!-- 显示模型输出 -->
              <div class="font-medium mb-1">{{ msg.content }}</div>

              <!-- 如果有检索文档则显示标题 -->
              <div v-if="msg.source_docs?.length" class="text-xs text-gray-500 mt-1">🔍 相关文档：</div>

            </div>
          </div>

          <!-- 如果消息包含来源文档（RAG），则在消息下方显示文档片段 -->
          <div v-if="msg.source_docs?.length" class="mt-2 text-xs text-gray-600 space-y-1 w-full">
            <!-- 遍历 source_docs，显示来源、页码和文本摘要 -->
            <div
              v-for="(doc, i) in msg.source_docs"
              :key="i"
              class="p-2 bg-gray-100 rounded-lg"
            >
              📄 来源: {{ doc.source }} 页码: {{ doc.page_num }}<br />
              {{ doc.text.slice(0, 150) }}...
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区：多行输入框 + 发送按钮 -->
      <div class="flex items-end space-x-3">
        <!-- 文本输入框，绑定 userInput，按 Enter 发送，Shift+Enter 换行 -->
        <textarea
          v-model="userInput"
          placeholder="输入内容后按 Enter 发送..."
          rows="2"
          class="flex-1 p-3 border border-gray-300 rounded-2xl resize-none bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition"
          @keyup.enter.exact.prevent="sendMessage"
          @keyup.shift.enter.stop
        ></textarea>
        <!-- 发送按钮：调用 sendMessage，loading 状态禁用按钮 -->
        <button
          @click="sendMessage"
          :disabled="loading || ragLoading"
          class="px-5 py-2.5 bg-blue-500 text-white rounded-2xl font-semibold shadow-md hover:bg-blue-600 transition disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {{ (isKnowledgeMode && ragLoading) || loading ? '发送中...' : '发送 🚀' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
/* 导入 Vue 的组合式 API：ref、computed、nextTick、onMounted */
import { ref, computed, nextTick, onMounted } from 'vue'
/* 导入 axios 用于 HTTP 请求 */
import axios from 'axios'

/* 定义后端 API 基础地址（请根据实际后端地址修改） */
const API_BASE = 'http://10.255.1.89:8001/api'

/* 会话列表（响应式引用） */
const sessions = ref([])
/* 当前会话 ID（响应式引用） */
const currentSessionId = ref(null)
/* 计算属性：根据 currentSessionId 找到当前会话对象 */
const currentSession = computed(() => sessions.value.find(s => s.id === currentSessionId.value))
/* 用户输入内容（响应式引用） */
const userInput = ref('')
/* 发送消息或请求时的加载状态（通用） */
const loading = ref(false)
/* RAG 请求专用加载状态（用于知识库查询按钮） */
const ragLoading = ref(false)
/* 知识库模式开关：按下时为 true（调用 /api/rag_chat），未按下为 false（调用 /api/chat）*/
const isKnowledgeMode = ref(false)

onMounted(async () => {
  try {
    // 先加载历史会话列表
    await loadSessions()

    // 获取最近会话
    const res = await axios.get(`${API_BASE}/get_last_session`)
    if (res.data.session_id) {
      // 在历史会话中查找这个 session
      const exist = sessions.value.find(s => s.id === res.data.session_id)
      if (exist) {
        currentSessionId.value = exist.id
      } else {
        // 如果历史列表里没有，就新建
        currentSessionId.value = res.data.session_id
        sessions.value.unshift({ id: currentSessionId.value, messages: [], title: `会话 ${currentSessionId.value}` })
      }
      await loadChatHistory(currentSessionId.value)
    } else {
      // 没有最近会话，新建
      await newChat()
    }
  } catch (e) {
    console.error("❌ 初始化会话失败:", e)
    await newChat()
  }

  // 加载 PDF 列表
  loadPdfList()
})


// 加载聊天记录
async function loadChatHistory(id) {
  try {
    const res = await axios.get(`http://10.255.1.89:8001/api/get_chat_history?session_id=${id}`)
    messages.value = res.data.messages || []
  } catch (e) {
    console.error("⚠️ 加载历史失败:", e)
  }
}

// 生成随机会话ID
function generateNewSessionId() {
  return "session_" + Math.random().toString(36).substring(2, 10)
}



/* 用于引用聊天容器 DOM，以便滚动到底部 */
const chatContainer = ref(null)
/* 控制左侧会话列表是否显示 */
const showList = ref(true)

/* PDF 文件列表（已上传的） */
const pdfList = ref([])
/* 上传状态标志：是否正在上传 */
const uploading = ref(false)
/* 上传成功标志 */
const uploadSuccess = ref(false)
/* 上传错误信息 */
const uploadError = ref('')

/* Milvus 处理的状态：是否在处理 */
const processing = ref(false)
/* 处理成功标志 */
const processSuccess = ref(false)
/* 处理错误信息 */
const processError = ref('')
/* Milvus 集合名，默认值 medical_papers */
const collectionName = ref('medical_papers')
/* Milvus db_path，默认值 A.db */
const dbPath = ref('A.db')

/* ---------------- 上传 PDF 相关方法 ---------------- */

/* 触发隐藏的文件输入框点击，弹出文件选择对话框 */
const triggerFileSelect = () => document.getElementById('pdfInput').click()

/* 处理文件选择事件并上传 PDF */
const handlePdfUpload = async (event) => {
  /* 从事件中取第一个文件 */
  const file = event.target.files[0]
  if (!file) return
  /* 仅允许 PDF */
  if (file.type !== 'application/pdf') {
    uploadError.value = '仅支持 PDF 文件'
    return
  }

  /* 设置上传状态 */
  uploading.value = true
  uploadSuccess.value = false
  uploadError.value = ''

  /* 使用 FormData 封装文件 */
  const formData = new FormData()
  formData.append('file', file)

  try {
    /* 通过 axios 上传文件到后端的 upload_pdf 接口 */
    const res = await axios.post(`${API_BASE}/upload_pdf`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    /* 根据后端返回判断是否成功 */
    if (res.data.success) {
      uploadSuccess.value = true
      /* 上传成功后刷新已上传文件列表 */
      await loadPdfList()
    } else {
      uploadError.value = res.data.error || '上传失败'
    }
  } catch (err) {
    /* 捕获网络或其他错误 */
    uploadError.value = '上传错误，请检查网络或服务器'
  } finally {
    /* 无论成功失败都结束上传 loading 状态 */
    uploading.value = false
  }
}

/* ---------------- 获取已上传 PDF 列表 ---------------- */

/* 向后端请求已上传的 PDF 列表并赋值给 pdfList */
const loadPdfList = async () => {
  try {
    const res = await axios.get(`${API_BASE}/list_pdfs`)
    pdfList.value = res.data || []
  } catch (err) {
    console.error('加载 PDF 列表失败:', err)
  }
}

/* ---------------- PDF 转向量并存入 Milvus ---------------- */

/* 触发后端处理已上传 PDF，将文本向量化并存入 Milvus */
const processPdfs = async () => {
  /* 校验集合名是否为空 */
  if (!collectionName.value.trim()) {
    processError.value = '请先输入 Milvus 集合名'
    return
  }

  /* 设置处理状态 */
  processing.value = true
  processSuccess.value = false
  processError.value = ''

  try {
    /* 向后端发送处理请求，包含 collection_name、db_path 和模型路径（可根据实际调整） */
    const res = await axios.post(`${API_BASE}/process_pdfs`, {
      collection_name: collectionName.value.trim(),
      db_path: dbPath.value,
      model_path: '/home/ldf/bigmodel/ChatGLM3/rag/paraphrase-multilingual-MiniLM-L12-v2'
    })

    /* 根据后端返回判断处理是否成功 */
    if (res.data.status === 'success') {
      processSuccess.value = true
    } else {
      processError.value = res.data.message || '处理失败'
    }
  } catch (err) {
    processError.value = '处理出错，请检查后端或网络'
  } finally {
    processing.value = false
  }
}

/* ---------------- 历史会话相关方法 ---------------- */

/* 切换左侧会话列表的显示/隐藏 */
const toggleList = () => { showList.value = !showList.value }

/* 从后端加载历史会话并设置当前会话为第一项（如果存在） */
const loadSessions = async () => {
  try {
    const res = await axios.get(`${API_BASE}/sessions`)
    sessions.value = res.data
    currentSessionId.value = sessions.value[0]?.id || null
  } catch (err) {
    console.error('加载历史会话失败:', err)
  }
}

/* 新建会话：向后端 post 创建会话，然后把新会话加到会话列表顶部并设置为当前会话 */
const newChat = async () => {
  try {
    const res = await axios.post(`${API_BASE}/sessions`, { title: `会话 ${sessions.value.length + 1}` })
    const newSession = { ...res.data, messages: [], latest_message: '' }
    sessions.value.unshift(newSession)
    currentSessionId.value = newSession.id
  } catch (err) {
    console.error('新建会话失败:', err)
  }
}

/* 选择某个会话：设置 currentSessionId 并在 DOM 更新后滚动到底部 */
const selectSession = async (id) => {
  currentSessionId.value = id
  await nextTick(scrollToBottom)
}

/* 切换知识库模式（按钮点击切换） */
const toggleKnowledgeMode = () => {
  // 切换模式状态；如果打开就变绿，若正在执行 RAG 请求则禁止切换
  if (ragLoading.value) return
  isKnowledgeMode.value = !isKnowledgeMode.value
}

/* ---------------- 聊天发送/接收逻辑 ---------------- */

/* 发送消息函数：根据 isKnowledgeMode 决定调用 /api/chat 或 /api/rag_chat */
const sendMessage = async () => {
  /* 获取并去除首尾空白的输入内容 */
  const content = userInput.value.trim()
  /* 如果内容为空或没有当前会话，则不发送 */
  if (!content || !currentSession.value) return

  /* 创建用户消息对象并加入当前会话消息数组 */
  const userMsg = { role: 'user', content }
  currentSession.value.messages.push(userMsg)

  /* 创建一个占位助手消息（正在处理提示），先插入到消息数组中 */
  const placeholder = { role: 'assistant', content: isKnowledgeMode.value ? '🤖 正在从知识库检索中，请稍候...' : '🤖 正在思考中，请稍候...', source_docs: [] }
  currentSession.value.messages.push(placeholder)

  /* 清空输入框并设置相应的 loading 状态，然后滚动到底部 */
  userInput.value = ''
  // 如果是知识库模式，使用 ragLoading；否则使用普通 loading
  if (isKnowledgeMode.value) {
    ragLoading.value = true
  } else {
    loading.value = true
  }
  await nextTick(scrollToBottom)

  try {
    if (isKnowledgeMode.value) {
      // 知识库模式 -> 调用 /api/rag_chat
      const res = await axios.post(`${API_BASE}/rag_chat`, {
        prompt: content,
        session_id: currentSessionId.value,
        collection_name: collectionName.value,
        milvus_db_path: dbPath.value,
        top_k: 5
      })

      placeholder.content = res.data?.text || res.data?.answer || '⚠️ 无响应'
      if (Array.isArray(res.data?.top_documents)) {
        placeholder.source_docs = res.data.top_documents
      } else if (Array.isArray(res.data?.source_docs)) {
        placeholder.source_docs = res.data.source_docs
      }
    } else {
      // 普通聊天模式 -> 调用 /api/chat
      const res = await axios.post(`${API_BASE}/chat`, {
        prompt: content,
        session_id: currentSessionId.value
      })

      placeholder.content = res.data?.text || res.data?.answer || '⚠️ 无响应'
      // chat 接口一般不会返回检索文档，但如果返回则兼容处理
      if (Array.isArray(res.data?.top_documents)) {
        placeholder.source_docs = res.data.top_documents
      } else if (Array.isArray(res.data?.source_docs)) {
        placeholder.source_docs = res.data.source_docs
      }
    }

    /* 将用户消息和助手消息保存到后端消息存储（可选） */
    try {
      await axios.post(`${API_BASE}/messages`, {
        session_id: currentSessionId.value,
        role: 'user',
        content
      })

      await axios.post(`${API_BASE}/messages`, {
        session_id: currentSessionId.value,
        role: 'assistant',
        content: placeholder.content
      })
    } catch (saveErr) {
      // 保存失败不影响展示，仅打印日志
      console.warn('保存消息到后端失败：', saveErr)
    }
  } catch (err) {
    /* 如果调用失败，更新占位消息为错误提示 */
    placeholder.content = '⚠️ 调用接口出错，请检查后端或网络连接'
    console.error(err)
  } finally {
    /* 结束加载状态并滚动到底部 */
    ragLoading.value = false
    loading.value = false
    await nextTick(scrollToBottom)
  }
}

/* 将聊天容器滚动到最底部的工具函数 */
const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTo({ top: chatContainer.value.scrollHeight, behavior: 'smooth' })
  }
}

/* 组件挂载时，加载历史会话和已上传 PDF 列表 */
onMounted(() => {
  loadSessions()
  loadPdfList()
})
</script>

<style scoped>
/* 自定义聊天容器滚动条宽度 */
.chat-container::-webkit-scrollbar {
  width: 8px;
}
/* 自定义滚动条滑块样式 */
.chat-container::-webkit-scrollbar-thumb {
  background-color: rgba(100, 100, 100, 0.3);
  border-radius: 4px;
}
</style>
