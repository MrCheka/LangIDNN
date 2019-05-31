<template>
  <a-layout-header class="header">
    <h1>{{msg}}</h1>
  </a-layout-header>
</template>

<script>
export default {
  name: "Header",
  data() {
    return {
      msg: "Language identification with Neural Networks"
    };
  }
};
</script>

<style scoped>
h1 {
  font-weight: normal;
  text-align: center;
  color: #ffffff;
  font-family: "Snell Roundhand", cursive;
}

.header {
  position: fixed;
  z-index: 10;
  width: 100%;
}

@media (max-width: 700px) {
  .header {
    height: 128px;
  }
}
</style>
