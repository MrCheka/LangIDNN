<template>
  <a-layout-content class="content">
    <a-collapse :bordered="false">
      <a-collapse-panel v-if="showLangs" header="Поддерживаемые языки" key="1" :style="customStyle">
        <p>{{langsStr}}</p>
      </a-collapse-panel>
    </a-collapse>
    <a-textarea
      placeholder="Введите текст"
      v-model="text"
      :autosize="{ minRows: 20, maxRows: 24 }"
    />
    <a-button
      v-on:click="detectLang"
      :loading="loadingButton"
      type="primary"
      :style="buttonStyle"
    >Определить!</a-button>
    <h1 v-if="showResult">Результат - {{resultLang}}. Точность определения - {{acc}}%.</h1>
  </a-layout-content>
</template>

<script>
import axios from "axios";

export default {
  name: "Main",
  data() {
    return {
      endpoint: "https://dd6d4513.ngrok.io",
      langs: null,
      langsStr: null,
      showLangs: false,
      showResult: false,
      text: null,
      resultLang: null,
      acc: null,
      customStyle:
        "background: #f7f7f7;border-radius: 4px;margin-bottom: 24px;margin-top: 10px;border: 0;overflow: hidden; text-align: justify;",
      buttonStyle: "width: 100%; margin-top: 10px;",
      loadingButton: false
    };
  },

  created() {
    this.getLangs();
  },

  methods: {
    getLangs() {
      this.showLangs = false;
      this.langsStr = null;

      axios
        .get(this.endpoint + "/getLangs")
        .then(response => {
          this.showLangs = true;
          this.langs = response.data.langs;
          var tmp = [];
          for (var lang in this.langs) {
            tmp.push(this.langs[lang]);
          }
          this.langsStr = Array.join(tmp, ", ");
        })
        .catch(error => {
          console.log("---error---");
          console.log(error);
        });
    },

    detectLang() {
      this.showResult = false;
      this.loadingButton = true;

      axios
        .post(this.endpoint + "/detectLang", {
          text: this.text
        })
        .then(response => {
          this.showResult = true;
          this.resultLang = response.data.lang;
          this.acc = response.data.acc;
          this.loadingButton = false;
        })
        .catch(error => {
          console.log("---error---");
          console.log(error);
          this.loadingButton = false;
        });
    }
  }
};
</script>

<style scoped>
.content {
  margin-top: 64px;
  padding: 0 50px 0 50px;
}

@media (max-width: 700px) {
  .content {
    margin-top: 128px;
  }
}
</style>
