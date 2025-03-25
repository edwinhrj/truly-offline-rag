<template>
  <div class="demo">
    <h1>DEMO: {{ message }}</h1>
    <button @click="create">DEMO: populate sqlite-vec</button>
    <button @click="fetchsqlite">DEMO: fetch most similar vector</button>
  </div>

  <div class="upload"><Upload /></div>
</template>

<script>
import axios from "axios";
import Upload from "./components/Upload.vue";

export default {
  data() {
    return {
      message: "loading...",
    };
  },
  components: {
    Upload,
  },
  methods: {
    async create() {
      try {
        await axios.post("http://localhost:8000/demo/create");
      } catch (error) {
        console.log("error:", error);
        this.message = "failed to populate sqlite";
      }
    },
    async fetchsqlite() {
      try {
        const response = await axios.post("http://localhost:8000/demo/sqlite");
        this.message = response.data;
      } catch (error) {
        console.log("error:", error);
      }
    },
  },
};
</script>

<style scoped>
.upload {
  margin-top: 200px;
}
</style>
