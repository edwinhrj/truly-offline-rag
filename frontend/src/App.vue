<template>
  <div class="upload">
    <h3>漫调AI(使用QWEN2.5 1B)</h3>
    <FileUpload></FileUpload>
  </div>

  <div class="query">
    <UserQuery></UserQuery>
  </div>
</template>

<script>
import FileUpload from "./components/FileUpload.vue";
import UserQuery from "./components/UserQuery.vue";

export default {
  components: {
    FileUpload,
    UserQuery,
  },
};
</script>

<style scoped></style>
