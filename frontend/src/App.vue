<template>
  <div class="upload">
    <h3>漫调AI(使用QWEN2.5 1B)</h3>
    <Upload />
  </div>

  <div class="query">
    <Query />
  </div>
</template>

<script>
import Upload from "./components/Upload.vue";
import Query from "./components/Query.vue";

export default {
  components: {
    Upload,
    Query,
  },
};
</script>

<style scoped></style>
