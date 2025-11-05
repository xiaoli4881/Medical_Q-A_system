<template>
  <div class="flex h-[90vh] mt-10 bg-gray-100 rounded-2xl shadow-xl overflow-hidden border border-gray-200">
    <!-- 左侧边栏 -->
    <div
      class="flex flex-col bg-white border-r border-gray-200 w-72 transition-all duration-300"
    >
      <!-- 顶部按钮区 -->
      <div class="flex flex-col items-start space-y-3 p-4 border-b bg-gray-50">
        <h2 class="text-lg font-semibold text-gray-800">💬 会话列表</h2>

        <button
          @click="loadSessions"
          class="w-full text-sm bg-gray-300 text-gray-800 px-3 py-2 rounded-lg hover:bg-gray-400 transition text-left"
        >
          📂 历史会话
        </button>

        <button
          @click="newChat"
          class="w-full text-sm bg-gradient-to-r from-purple-500 to-indigo-500 text-white px-3 py-2 rounded-lg hover:opacity-90 transition text-left"
        >
          ✨ 新对话
        </button>

        <button
          @click="toggleList"
          class="w-full text-sm bg-gray-200 text-gray-800 px-3 py-2 rounded-lg hover:bg-gray-300 transition text-left"
        >
          {{ showList ? '⬅️ 收起' : '➡️ 展开' }}
        </button>
      </div>

      <!-- ✅ 历史会话列表 -->
      <div
        v-show="showList"
        class="flex-1 p-2 space-y-2 overflow-auto transition-all duration-300"
      >
        <div
          v-for="session in sessions"
          :key="session.id"
          class="flex items-center justify-between group"
        >
          <div
            @click="selectSession(session.id)"
            class="flex-1 p-3 rounded-lg cursor-pointer text-sm font-medium transition-all truncate"
            :class="session.id === currentSessionId
              ? 'bg-blue-500 text-white shadow-md'
              : 'hover:bg-gray-100 text-gray-700'"
          >
            <div class="font-semibold truncate">{{ session.title || '未命名对话' }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧聊天主界面 -->
    <div class="flex flex-col flex-1 p-6 bg-gray-50 transition-all duration-300">
      <div class="flex justify-between items-center mb-4">
        <h1 class="text-2xl font-semibold text-gray-800">🤖 大模型交互界面</h1>
        <div class="text-gray-500 text-sm">
          当前会话：{{ currentSession?.title || '新会话' }}
        </div>
      </div>

      <!-- 聊天记录 -->
      <div
        ref="chatContainer"
        class="flex-1 overflow-y-auto mb-4 p-4 bg-white rounded-2xl shadow-inner chat-container relative"
      >
        <div v-if="!currentSession?.messages?.length" class="text-center text-gray-400 mt-20">
          💬 还没有开始聊天，试着输入点什么吧~
        </div>

        <div
          v-for="(msg, index) in currentSession?.messages || []"
          :key="index"
          class="flex mb-4"
          :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div
            v-if="msg.role === 'assistant'"
            class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3 text-blue-500 font-bold"
          >
            🤖
          </div>
          <div
            v-if="msg.role === 'user'"
            class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center ml-3 text-green-500 font-bold order-2"
          >
            🧑
          </div>
          <div
            :class="[ 
              'max-w-[70%] px-4 py-3 rounded-2xl text-sm shadow-md break-words transition-all duration-200',
              msg.role === 'user'
                ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-br-none'
                : 'bg-gray-200 text-gray-800 rounded-bl-none'
            ]"
          >
            {{ msg.content }}
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="flex items-end space-x-3">
        <textarea
          v-model="userInput"
          placeholder="输入内容后按 Enter 发送..."
          rows="2"
          class="flex-1 p-3 border border-gray-300 rounded-2xl resize-none bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition"
          @keyup.enter.exact.prevent="sendMessage"
          @keyup.shift.enter.stop
        ></textarea>
        <button
          @click="sendMessage"
          :disabled="loading"
          class="px-5 py-2.5 bg-blue-500 text-white rounded-2xl font-semibold shadow-md hover:bg-blue-600 transition disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {{ loading ? '发送中...' : '发送 🚀' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import axios from 'axios'

const API_BASE = 'http://10.255.1.89:8001/api'

const sessions = ref([])
const currentSessionId = ref(null)
const currentSession = computed(() => sessions.value.find(s => s.id === currentSessionId.value))
const userInput = ref('')
const loading = ref(false)
const chatContainer = ref(null)

// ✅ 控制“历史会话内容”是否显示
const showList = ref(true)
const toggleList = () => { showList.value = !showList.value }

// ---------------- 加载历史会话 ----------------
const loadSessions = async () => {
  try {
    const res = await axios.get(`${API_BASE}/sessions`)
    sessions.value = res.data
    currentSessionId.value = sessions.value[0]?.id || null
  } catch (err) {
    console.error('加载历史会话失败:', err)
  }
}

// ---------------- 新建会话 ----------------
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

// ---------------- 删除会话 ----------------
const deleteSession = async (id) => {
  if (!confirm('确定要删除此会话吗？')) return
  try {
    await axios.delete(`${API_BASE}/sessions/${id}`)
    sessions.value = sessions.value.filter(s => s.id !== id)
    currentSessionId.value = sessions.value[0]?.id || null
  } catch (err) {
    console.error('删除会话失败:', err)
  }
}

// ---------------- 选择会话 ----------------
const selectSession = async (id) => {
  currentSessionId.value = id
  try {
    const res = await axios.get(`${API_BASE}/sessions/${id}`)
    const index = sessions.value.findIndex(s => s.id === id)
    if (index !== -1) {
      sessions.value[index].messages = res.data.messages
      sessions.value[index].latest_message = res.data.messages?.[res.data.messages.length - 1]?.content || ''
    }
  } catch (err) {
    console.error('加载会话消息失败:', err)
  }
  await nextTick(scrollToBottom)
}

// ---------------- 发送消息 ----------------
const sendMessage = async () => {
  const content = userInput.value.trim()
  if (!content || !currentSession.value) return

  const userMsg = { role: 'user', content }
  currentSession.value.messages.push(userMsg)

  const placeholder = { role: 'assistant', content: '🤖 正在思考中，请稍候...' }
  currentSession.value.messages.push(placeholder)

  userInput.value = ''
  loading.value = true
  await nextTick(scrollToBottom)

  try {
    const res = await axios.post(`${API_BASE}/chat`, {
      prompt: content,
      session_id: currentSessionId.value
    })
    placeholder.content = res.data?.text || '⚠️ 无响应'

    const index = sessions.value.findIndex(s => s.id === currentSessionId.value)
    if (index !== -1) sessions.value[index].latest_message = placeholder.content
  } catch (err) {
    console.error('调用接口失败:', err)
    placeholder.content = '⚠️ 调用接口出错，请检查后端或网络连接'
  } finally {
    loading.value = false
    await nextTick(scrollToBottom)
  }
}

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTo({ top: chatContainer.value.scrollHeight, behavior: 'smooth' })
  }
}
</script>

<style scoped>
.chat-container::-webkit-scrollbar {
  width: 8px;
}
.chat-container::-webkit-scrollbar-thumb {
  background-color: rgba(100, 100, 100, 0.3);
  border-radius: 4px;
}
</style>
