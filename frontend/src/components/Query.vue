<template>
  <div class="qa-container">
    <div class="qa-input">
      <input
        v-model="query"
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

<script>
import axios from "axios";

export default {
  data() {
    return {
      query: "",
      answer: "",
    };
  },
  methods: {
    async handleAsk() {
      if (!this.query.trim()) return;

      try {
        const response = await axios.post("http://localhost:8000/query/ask", {
          query: this.query,
        });
        // Assume the backend returns the answer in response.data.answer
        this.answer = response.data;
      } catch (error) {
        console.error("Error during request:", error);
        this.answer = "获取答案时出错。请再试一次。";
      }
    },
  },
};
</script>

<style scoped></style>
