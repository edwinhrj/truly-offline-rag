<template>
  <div>
    <input
      ref="fileInput"
      type="file"
      accept="application/pdf"
      style="display: none"
      @change="handleFileUpload"
    />
    <button @click="triggerFileInput">传PDF文件</button>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "FileUpload",
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click();
    },

    // handle server accepting the uploaded pdf file
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await axios.post(
          "http://localhost:8000/sqlite/upload",
          formData
        );
        console.log("Upload successful:", response.data);
      } catch (error) {
        console.error("Error uploading file:", error);
      }
    },
  },
};
</script>

<style scoped></style>
