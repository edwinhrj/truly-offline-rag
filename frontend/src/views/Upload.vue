<template>
  <div class="container">
    <h1>PyQt6 与 Web 前端集成示例</h1>
    <p>这是一个使用 PyQt6 的 QWebEngineView 显示的 HTML 页面，通过 Flask API 通信。</p>
    
    <div class="section">
      <h2>PDF文件上传</h2>
      <p>选择并上传PDF文件到后端进行处理和存储:</p>
      <input type="file" accept=".pdf" @change="handleFileChange" />
      <div class="file-info">{{ fileInfo }}</div>
      
      <button @click="uploadPdf" :disabled="!selectedFile">上传PDF文件</button>
      <button class="danger" @click="clearDatabase">清除数据库</button>
      
      <progress v-if="uploading" :value="uploadProgress" max="100"></progress>
    </div>
    
    <div id="result">
      <p v-if="resultText">{{ resultText }}</p>
      <p v-else>结果将显示在这里...</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const API_BASE_URL = 'http://127.0.0.1:8080'

const fileInfo = ref('未选择文件')
const selectedFile = ref(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const resultText = ref('')

// Handle file selection
const handleFileChange = (event) => {
  const files = event.target.files
  if (files.length > 0) {
    const file = files[0]
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      fileInfo.value = '错误: 请选择PDF文件'
      selectedFile.value = null
      return
    }
    fileInfo.value = `已选择: ${file.name} (${formatFileSize(file.size)})`
    selectedFile.value = file
  } else {
    fileInfo.value = '未选择文件'
    selectedFile.value = null
  }
}

// Upload PDF file to backend
const uploadPdf = () => {
  if (!selectedFile.value) return

  const formData = new FormData()
  formData.append('file', selectedFile.value)
  
  uploading.value = true
  uploadProgress.value = 0
  resultText.value = '正在上传文件，请稍候...'
  
  const xhr = new XMLHttpRequest()
  
  // Track upload progress
  xhr.upload.addEventListener('progress', (e) => {
    if (e.lengthComputable) {
      uploadProgress.value = (e.loaded / e.total) * 100
    }
  })
  
  xhr.onreadystatechange = () => {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      uploading.value = false
      if (xhr.status === 200) {
        try {
          const response = JSON.parse(xhr.responseText)
          resultText.value = `成功: ${response.message}\n${JSON.stringify(response, null, 2)}`
          // Reset file input
          selectedFile.value = null
          fileInfo.value = '未选择文件'
        } catch (e) {
          resultText.value = `解析响应时出错: ${e}`
        }
      } else {
        let errorMessage = '上传失败'
        let errorDetails = ''
        try {
          const response = JSON.parse(xhr.responseText)
          errorMessage = response.message || errorMessage
          errorDetails = response.error_details || ''
        } catch (e) {
          errorMessage = `上传失败: ${xhr.status} ${xhr.statusText}`
        }
        resultText.value = `错误: ${errorMessage}\n${errorDetails}`
      }
    }
  }
  
  xhr.onerror = () => {
    uploading.value = false
    resultText.value = '网络错误: 无法连接到服务器，请检查网络连接。'
  }
  
  xhr.open('POST', `${API_BASE_URL}/sqlite/upload`, true)
  xhr.send(formData)
}

// Clear the database via backend endpoint
const clearDatabase = async () => {
  if (!confirm('确定要清除数据库吗？此操作不可撤销！')) {
    return
  }
  resultText.value = '正在清除数据库，请稍候...'
  try {
    const response = await fetch(`${API_BASE_URL}/sqlite/clear`, { method: 'POST' })
    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`)
    const data = await response.json()
    resultText.value = `成功: ${data.message}`
  } catch (error) {
    resultText.value = `错误: ${error.message}`
    console.error('Clear DB error:', error)
  }
}

// Helper function to format file sizes
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style scoped>
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 20px;
  background-color: #f5f5f5;
}
.container {
  max-width: 800px;
  margin: 0 auto;
  background-color: white;
  padding: 20px;
  border-radius: 5px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
h1, h2, h3 {
  color: #333;
}
button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px 15px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 4px;
}
button:hover {
  background-color: #45a049;
}
button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
#result {
  margin-top: 20px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f9f9f9;
  min-height: 100px;
}
input[type="text"] {
  width: 100%;
  padding: 12px 20px;
  margin: 8px 0;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}
.section {
  margin-top: 30px;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 5px;
}
.file-info {
  margin: 10px 0;
  font-style: italic;
}
progress {
  width: 100%;
  height: 20px;
  margin-top: 10px;
}
.danger {
  background-color: #f44336;
}
.danger:hover {
  background-color: #d32f2f;
}
</style>
