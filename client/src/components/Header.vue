<template>
  <div class="header">
    <header>
      <h1>{{msg}}</h1>
    </header>
  </div>
</template>

<script>
export default {
  name: 'Header',
  data () {
    return {
      msg: 'Language identification with Neural Networks'
    }
  }
}
</script>

<style scoped>
h1, h2 {
  font-weight: normal;
}

header {
  position: fixed;
  top: 0;
  width: 100%;
  min-height: 90px;
  border-bottom: 1px solid #42b983;
  text-align: center;
  background: #ffffff;
}
</style>
