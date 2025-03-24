<template>
  <div>
    <h1>{{ message }}</h1>
    <button @click="create">populate sqlite-vec</button>
    <button @click="fetchsqlite">fetch most similar vector</button>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      message: "loading...",
    };
  },
  methods: {
    async create() {
      try {
        await axios.get("http://localhost:8000/create");
      } catch (error) {
        console.log("error:", error);
        this.message = "failed to populate sqlite";
      }
    },
    async fetchsqlite() {
      try {
        const response = await axios.get("http://localhost:8000/sqlite");
        this.message = response.data;
      } catch (error) {
        console.log("error:", error);
      }
    },
  },
};
</script>
