<template>
  <a-layout>
    <Header/>
    <Main/>
    <Footer/>
  </a-layout>
</template>

<script>
import Header from "./components/Header";
import Main from "./components/Main";
import Footer from "./components/Footer";

export default {
  name: "App",
  components: {
    Header,
    Main,
    Footer
  }
};
</script>

<style>
</style>
