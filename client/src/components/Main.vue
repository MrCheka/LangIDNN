<template>
  <a-layout-content class="content">
    <a-collapse :bordered="false">
      <a-collapse-panel v-if="showLangs" header="Поддерживаемые языки" key="1" :style="customStyle">
        <p>{{langsStr}}</p>
      </a-collapse-panel>
    </a-collapse>
    <label>Текст:</label>
    <a-radio-group :value="multi" @change="handleMultiChange">
      <a-radio-button value="false">Одноязычный</a-radio-button>
      <a-radio-button value="true">Многоязычный</a-radio-button>
    </a-radio-group>
    <label v-if="multi == 'true'">Количество языков:</label>
    <a-select
      v-if="multi == 'true'"
      defaultValue="1"
      style="width: 60px"
      @change="handleCountChange"
    >
      <a-select-option value="1">1</a-select-option>
      <a-select-option value="2">2</a-select-option>
      <a-select-option value="3">3</a-select-option>
      <a-select-option value="4">4</a-select-option>
      <a-select-option value="5">5</a-select-option>
      <a-select-option value="6">6</a-select-option>
      <a-select-option value="7">7</a-select-option>
    </a-select>
    <br>
    <br>
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
    <h2 v-if="multiResult" style="text-align: center;">{{multiResult}}</h2>
    <h3 v-if="showResult" style="white-space:pre-wrap;">{{result}}</h3>
  </a-layout-content>
</template>

<script>
import axios from "axios";

export default {
  name: "Main",
  data() {
    return {
      endpoint: "http://127.0.0.1:8888",
      langs: null,
      langsStr: null,
      showLangs: false,
      showResult: false,
      text: null,
      multiResult: null,
      result: null,
      customStyle:
        "background: #f7f7f7;border-radius: 4px;margin-bottom: 24px;margin-top: 10px;border: 0;overflow: hidden; text-align: justify;",
      buttonStyle: "width: 100%; margin-top: 10px;",
      loadingButton: false,
      multi: "false",
      count: "1"
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
      this.multiResult = null;

      axios
        .post(this.endpoint + "/detectLangs", {
          text: this.text,
          multi: this.multi == "true",
          count: parseInt(this.count)
        })
        .then(response => {
          this.showResult = true;
          this.result = "";

          if (this.multi == "true")
            this.multiResult = "Найдено языков - " + response.data.count;
          console.log(response.data);
          for (var i = 0; i < response.data.result.length; i++) {
            this.result += "Язык - " + response.data.result[i].lang;
            this.result += ". Вероятность - " + response.data.result[i].acc;
            this.result += "%.\n";
          }

          this.loadingButton = false;
        })
        .catch(error => {
          console.log("---error---");
          console.log(error);
          this.loadingButton = false;
        });
    },

    handleMultiChange(e) {
      this.multi = e.target.value;
    },

    handleCountChange(value) {
      this.count = value;
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
