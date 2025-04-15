<template>
  <div class="home-container">
    <h1>AI桌面应用程序</h1>
    
    <div v-if="loading" class="setup-container">
      <div class="status-message">
        {{ currentStage.message }}
        <span v-if="currentStage.percent !== null" class="percent">
          ({{ currentStage.percent }}%)
        </span>
      </div>
      
      <div class="progress-container">
        <progress 
          class="progress-bar" 
          :value="currentStage.percent || 0" 
          max="100"
        ></progress>
        
        <div class="stage-tracker">
          <div v-for="stage in stages" :key="stage.key" 
               :class="['stage', { 
                 'active': stage.active, 
                 'completed': stage.completed,
                 'pending': !stage.active && !stage.completed
               }]">
            <div class="stage-icon">
              <span v-if="stage.completed" class="completed-icon">✓</span>
              <span v-else-if="stage.active" class="active-icon">⟳</span>
              <span v-else class="pending-icon">•</span>
            </div>
            <div class="stage-label">{{ stage.label }}</div>
            <div v-if="stage.active" class="stage-progress">
              {{ currentStage.percent }}%
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="error" class="error-container">
      <div class="error-message">
        <span class="error-icon">⚠️</span>
        {{ error }}
      </div>
      <button class="retry-button" @click="retrySetup">
        <span class="retry-icon">↻</span> 重试安装
      </button>
    </div>
    
    <div v-else class="setup-complete">
      <div class="success-message">
        <span class="success-icon">🎉</span>
        <h2>安装完成!</h2>
      </div>
      <p>Ollama和AI模型已准备就绪。</p>
      <router-link to="/chat" class="start-chat-button">
        开始对话 →
      </router-link>
      
      <div class="system-status">
        <div class="status-item">
          <span class="status-icon success">✓</span>
          Ollama 已安装
        </div>
        <div class="status-item">
          <span class="status-icon success">✓</span>
          Ollama 运行中
        </div>
        <div class="status-item">
          <span class="status-icon success">✓</span>
          模型已加载
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const emit = defineEmits(['setup-complete'])
const router = useRouter()

const loading = ref(true)
const error = ref(null)
const setupStatus = ref(null)

const stages = ref([
  { key: 'downloading', label: '下载Ollama', active: false, completed: false },
  { key: 'installing', label: '安装Ollama', active: false, completed: false },
  { key: 'starting', label: '启动服务', active: false, completed: false },
  { key: 'pulling_model', label: '下载模型', active: false, completed: false },
  { key: 'complete', label: '完成最后设置', active: false, completed: false }
])

const currentStage = computed(() => {
  if (!setupStatus.value?.progress) {
    return { message: '准备安装中...', percent: 0 }
  }
  
  const stageMessages = {
    'downloading': '正在下载Ollama安装程序',
    'downloading_cli_zip': '正在下载Ollama CLI',
    'cli_zip_exists': '检测到CLI文件',
    'extracting_cli_zip': '正在解压Ollama',
    'complete_installation': '安装完成',
    'installing': '正在安装Ollama',
    'starting': '正在启动Ollama服务',
    'pulling_model': '正在下载AI模型(可能需要几分钟)',
    'complete': '完成最后设置'
  }
  
  return {
    message: stageMessages[setupStatus.value.progress.stage] || '处理中...',
    percent: setupStatus.value.progress.progress || 0
  }
})

// Update stage states based on progress
watch(setupStatus, (newStatus) => {
  if (!newStatus?.progress) return
  
  const currentIndex = stages.value.findIndex(
    s => s.key === newStatus.progress.stage
  )
  
  stages.value.forEach((stage, index) => {
    stage.active = index === currentIndex
    stage.completed = index < currentIndex || 
                     (newStatus.progress.stage === 'complete' && index <= currentIndex)
  })
}, { deep: true })

const checkStatus = async () => {
  try {
    const response = await fetch('/api/status')
    if (!response.ok) throw new Error('Network response was not ok')
    
    const data = await response.json()
    setupStatus.value = data
    
    if (data.error) throw new Error(data.error)
    return data
  } catch (err) {
    error.value = `Status check failed: ${err.message}`
    throw err
  }
}

const setupOllama = async () => {
  try {
    const response = await fetch('/api/setup', {
      method: 'POST'
    })
    
    if (!response.ok) throw new Error('Network response was not ok')
    
    const data = await response.json()
    if (!data.success) throw new Error(data.message || 'Setup failed')
    
    return true
  } catch (err) {
    error.value = `Setup error: ${err.message}`
    throw err
  }
}

const pollStatus = async () => {
  try {
    while (loading.value) {
      const status = await checkStatus()
      
      // Check that:
      // - progress stage is "complete" at 100%
      // - Ollama is installed and running
      // - And all models (in status.modelsInstalled) are true.
      if (
        status &&
        status.progress &&
        status.progress.stage === 'complete' &&
        status.progress.progress === 100 &&
        status.ollamaInstalled &&
        status.ollamaRunning &&
        status.modelsInstalled &&
        Object.values(status.modelsInstalled).every(installed => installed === true)
      ) {
        loading.value = false
        emit('setup-complete')
        // Optionally, navigate automatically to a "completed" route:
        // router.push('/completed')
        break
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
  } catch (err) {
    loading.value = false
  }
}

const initializeApp = async () => {
  loading.value = true
  error.value = null
  
  try {
    const status = await checkStatus()
    
    // If Ollama or models are not yet set up, start the setup and poll the status.
    if (!(status.ollamaInstalled && status.ollamaRunning && status.modelsInstalled && Object.values(status.modelsInstalled).every(v => v === true))) {
      await setupOllama()
      pollStatus()
    } else {
      loading.value = false
      emit('setup-complete')
    }
  } catch (err) {
    loading.value = false
    if (!error.value) error.value = `Initialization error: ${err.message}`
  }
}

const retrySetup = () => {
  initializeApp()
}

onMounted(() => {
  initializeApp()
})
</script>

<style scoped>
.home-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

h1 {
  color: #2c3e50;
  margin-bottom: 2rem;
}

.setup-container {
  margin: 2rem 0;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.status-message {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  min-height: 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
}

.percent {
  color: #1976d2;
  font-weight: bold;
}

.progress-container {
  margin-top: 1.5rem;
}

.progress-bar {
  width: 100%;
  height: 12px;
  margin-bottom: 2rem;
  -webkit-appearance: none;
  appearance: none;
  border-radius: 6px;
  overflow: hidden;
}

.progress-bar::-webkit-progress-bar {
  background-color: #e9ecef;
}

.progress-bar::-webkit-progress-value {
  background-color: #1976d2;
  transition: width 0.5s ease;
}

.stage-tracker {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
  gap: 1rem;
}

.stage {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.stage-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.completed-icon {
  color: #4caf50;
}

.active-icon {
  color: #1976d2;
  animation: spin 1s linear infinite;
}

.pending-icon {
  color: #adb5bd;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.stage-label {
  font-size: 0.9rem;
  text-align: center;
  margin-bottom: 0.5rem;
}

.stage-progress {
  font-size: 0.8rem;
  font-weight: bold;
  color: #1976d2;
}

.stage.active {
  background-color: #e7f1ff;
}

.stage.completed {
  background-color: #e8f5e9;
}

.stage.pending {
  opacity: 0.7;
}

.error-container {
  margin: 2rem 0;
  padding: 1.5rem;
  background-color: #ffebee;
  border-radius: 10px;
  border-left: 4px solid #d32f2f;
}

.error-message {
  color: #d32f2f;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.error-icon {
  font-size: 1.3rem;
}

.retry-button {
  padding: 0.75rem 1.5rem;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 auto;
  transition: background-color 0.3s;
}

.retry-button:hover {
  background-color: #1565c0;
}

.retry-icon {
  font-size: 1.1rem;
}

.setup-complete {
  margin-top: 2rem;
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.success-message {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.success-icon {
  font-size: 1.8rem;
}

.start-chat-button {
  display: inline-block;
  padding: 0.8rem 1.8rem;
  background-color: #4caf50;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 500;
  margin: 1.5rem 0;
  transition: background-color 0.3s;
}

.start-chat-button:hover {
  background-color: #3d8b40;
}

.system-status {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: white;
  border-radius: 8px;
  text-align: left;
  max-width: 300px;
  margin: 2rem auto 0;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.8rem;
  font-size: 0.95rem;
}

.status-item:last-child {
  margin-bottom: 0;
}

.status-icon {
  width: 1.2rem;
  height: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.status-icon.success {
  color: #4caf50;
  font-weight: bold;
}
</style>