<template>
  <div class="chat-container">
    <div class="chat-header">
      <h1>与 Deepseek R1 对话</h1>
      <router-link to="/" class="back-button">← 返回首页</router-link>
    </div>
    
    <div class="chat-messages" ref="messagesContainer">
      <div v-for="(msg, index) in messages" :key="index" 
           :class="['message', msg.role]">
        <div class="message-content" v-html="formatMessage(msg.content)"></div>
        <div class="message-meta">
          {{ msg.timestamp }} • {{ msg.role === 'user' ? '你' : 'AI助手' }}
        </div>
      </div>
      
      <div v-if="isLoading" class="loading-indicator">
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
      </div>
    </div>
    
    <div v-if="error" class="error-message">{{ error }}</div>
    
    <div class="chat-input">
      <textarea
        v-model="userInput"
        placeholder="Type your message..."
        @keydown.enter.exact.prevent="sendMessage"
        :disabled="isLoading"
      ></textarea>
      <button @click="sendMessage" :disabled="isLoading || !userInput.trim()">
        {{ isLoading ? '发送中...' : '发送' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const messages = ref([
  {
    role: 'assistant',
    content: '你好！我是你的AI助手。今天有什么可以帮您的吗？',
    timestamp: new Date().toLocaleTimeString()
  }
])

const userInput = ref('')
const isLoading = ref(false)
const error = ref(null)
const messagesContainer = ref(null)

// Format message with markdown support
function formatMessage(text) {
  if (!text) return ''
  
  // Basic XSS protection
  let safeText = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // Markdown formatting
  safeText = safeText
    // Bold text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic text
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Convert triple backtick code blocks
    .replace(/```(\w*)\n([\s\S]*?)\n```/g, '<pre class="code-block"><code class="language-$1">$2</code></pre>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
    // Line breaks
    .replace(/\n/g, '<br>')
    // Links
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
  
  return safeText
}

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return
  
  const message = userInput.value.trim()
  userInput.value = ''
  error.value = null
  
  // Add user message
  messages.value.push({
    role: 'user',
    content: message,
    timestamp: new Date().toLocaleTimeString()
  })
  
  // Add empty assistant message
  const assistantMessage = {
    role: 'assistant',
    content: '',
    timestamp: new Date().toLocaleTimeString(),
    id: Date.now() // Unique ID for tracking
  }
  messages.value.push(assistantMessage)
  
  isLoading.value = true
  scrollToBottom()
  
  const msgIndex = messages.value.findIndex(m => m.id === assistantMessage.id)
  
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message })
    })
    
    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`)
    
    // Handle streaming response
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      
      if (msgIndex !== -1) {
        for (const line of lines) {
          if (line.trim()) {
            messages.value[msgIndex].content += line + '\n'
          }
        }
        scrollToBottom()
      }
    }
    
    // Add any remaining content
    if (buffer && msgIndex !== -1) {
      messages.value[msgIndex].content += buffer
      scrollToBottom()
    }
    
  } catch (err) {
    error.value = err.message
    if (msgIndex !== -1) {
      messages.value[msgIndex].content += `\n\nError: ${err.message}`
      scrollToBottom()
    }
  } finally {
    isLoading.value = false
  }
}

const scrollToBottom = () => {
  setTimeout(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }, 100)
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style>
.chat-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.back-button {
  text-decoration: none;
  color: #1976d2;
  font-size: 0.9rem;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  margin-bottom: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
  background-color: #fafafa;
}

.message {
  margin-bottom: 15px;
}

.message-content {
  padding: 12px 16px;
  border-radius: 18px;
  max-width: 80%;
  word-wrap: break-word;
  line-height: 1.5;
}

.message.user {
  display: flex;
  justify-content: flex-end;
}

.message.user .message-content {
  background-color: #1976d2;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant {
  display: flex;
  justify-content: flex-start;
}

.message.assistant .message-content {
  background-color: #f1f1f1;
  border-bottom-left-radius: 4px;
}

.message.system {
  display: flex;
  justify-content: center;
}

.message.system .message-content {
  background-color: #ffebee;
  color: #d32f2f;
  border-radius: 4px;
  font-size: 0.9rem;
}

.message-meta {
  font-size: 0.8rem;
  color: #999;
  margin-top: 4px;
}

.loading-indicator {
  text-align: center;
  padding: 10px;
}

.chat-input {
  display: flex;
  gap: 10px;
}

.chat-input textarea {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: none;
  min-height: 60px;
  font-family: inherit;
}

.chat-input button {
  padding: 0 20px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  height: 44px;
  align-self: flex-end;
}

.chat-input button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #d32f2f;
  background-color: #ffebee;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.loading-indicator {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 10px;
}

.loading-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #1976d2;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% { 
    transform: scale(0);
  } 40% { 
    transform: scale(1);
  }
}

/* Markdown-specific styles */
.message-content strong {
  font-weight: bold;
}

.message-content em {
  font-style: italic;
}

.code-block {
  background-color: #f6f8fa;
  padding: 1em;
  border-radius: 6px;
  overflow-x: auto;
  margin: 0.5em 0;
  font-family: 'Courier New', monospace;
  white-space: pre;
}

.code-block code {
  background-color: transparent;
  padding: 0;
  color: inherit;
}

.inline-code {
  font-family: 'Courier New', monospace;
  background-color: rgba(175, 184, 193, 0.2);
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
}

.message-content a {
  color: #1976d2;
  text-decoration: none;
}

.message-content a:hover {
  text-decoration: underline;
}
</style>