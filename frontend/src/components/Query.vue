<template>
  <div class="qa-container">
    <div class="qa-input">
      <input
        v-model="question"
        placeholder="请询问与贵公司相关的任何问题"
        @keydown.enter="handleAsk"
        autocomplete="off"
      />
      <button @click="handleAsk">问</button>
    </div>
    <div class="qa-output">
      <textarea
        v-model="answer"
        readonly
        placeholder="AI回答将在此显示"
      ></textarea>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";

const question = ref("");
const answer = ref("");

// When the user clicks "Ask" or presses Enter, send the question to the backend.
async function handleAsk() {
  if (!question.value.trim()) return;

  try {
    const response = await axios.post(
      "http://localhost:8000/query/ask",
      {
        question: question.value,
      },
      // send company name to backend to know which milvus collection to retrieve from
      { headers: { company } }
    );
    // Assume the backend returns the answer in response.data.answer
    answer.value = response.data;
  } catch (error) {
    console.error("Error during request:", error);
    answer.value = "获取答案时出错。请再试一次。";
  }
}
</script>

<style scoped></style>
