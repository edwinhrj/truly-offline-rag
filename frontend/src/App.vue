<template>
  <div class="upload">
    <h3>{{ message }}</h3>
    <button @click="fetchsqlite">fetch most similar sentence</button>
    <Upload />
  </div>

  <div class="query">
    <Query />
  </div>
</template>

<script>
import axios from "axios";
import Upload from "./components/Upload.vue";
import Query from "./components/Query.vue";

export default {
  data() {
    return {
      message: "(most similar sentence)",
    };
  },
  components: {
    Upload,
    Query,
  },
  methods: {
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

<style scoped></style>
