<template>
  <div class="app-container">
    <header class="app-header">
      <nav>
        <router-link to="/">首页</router-link>
        <router-link to="/chat" v-if="isSetupComplete">对话</router-link>
        <router-link to="/upload" v-if="isSetupComplete">上传</router-link>
      </nav>
      <div class="status-badge" :class="{ ready: isSetupComplete }">
        {{ isSetupComplete ? '准备就绪' : '设置中...' }}
      </div>
    </header>
    
    <router-view @setup-complete="handleSetupComplete" />
  </div>
</template>

<script setup>
import { ref } from 'vue'

const isSetupComplete = ref(false)

const handleSetupComplete = () => {
  isSetupComplete.value = true
}
</script>

<style>
.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  margin-bottom: 30px;
  border-bottom: 1px solid #eee;
}

nav {
  display: flex;
  gap: 20px;
}

nav a {
  text-decoration: none;
  color: #1976d2;
  font-weight: 500;
  padding: 5px 10px;
  border-radius: 4px;
}

nav a.router-link-exact-active {
  background-color: #1976d2;
  color: white;
}

.status-badge {
  padding: 5px 10px;
  background-color: #ffebee;
  color: #d32f2f;
  border-radius: 20px;
  font-size: 0.8rem;
}

.status-badge.ready {
  background-color: #e8f5e9;
  color: #2e7d32;
}
</style>