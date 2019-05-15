<template>
  <div class="main">
      <main>
        <span v-if="showLangs">Supported languages: {{langsStr}}</span>
        <span>Enter the text:</span>
        <textarea v-model="text" placeholder="some text"></textarea>
        <button v-on:click='detectLang' type="button">Send</button>
        <h2 v-if="showResult">Language: {{resultLang}}. Accuracy: {{acc}}</h2>
      </main>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Main',
  data () {
    return {
        endpoint: 'http://127.0.0.1:5000',
        langs: null,
        langsStr: null,
        showLangs: false,
        showResult: false,
        text: null,
        resultLang: null,
        acc: null
    }
  },

  created() {
      this.getLangs();
  },

  methods: {
      getLangs() {
          this.showLangs = false;
          this.langsStr = null;

          axios.get(this.endpoint + '/getLangs')
            .then(response => {
                this.showLangs = true;
                this.langs = response.data.langs;
                var tmp = [];
                this.langs.forEach(row => {
                    Object.keys(row).forEach(el => {
                        tmp.push(row[el]);
                    });
                });
                this.langsStr = Array.join(tmp, ', ');
            })
            .catch(error => {
                console.log('---error---');
                console.log(error);
            })
        },
    
    detectLang() {
        this.showResult = false;

        axios.post(this.endpoint + '/detectLang', {
            text: this.text
        })
        .then(response => {
            this.showResult = true;            
            this.resultLang = response.data.lang;
            this.acc = response.data.acc;
        })
        .catch(error => {
            console.log('---error---');
            console.log(error);
        })
    }
  }
}
</script>

<style scoped>
h1, h2 {
  font-weight: normal;
}

button {
  margin-top: 5px;
  margin-bottom: 5px;
  width: 95%;
  align-self: center;
}

span {
  align-self: flex-start;
  flex: 0 0 10px;
}

main {
  display: flex;
  flex-direction: column;
  text-align: center;
  height: calc(100vh - 90px);
  margin-top: 90px;
  margin-left: auto;
  margin-right: auto;
  overflow: hidden;
}

textarea {
  resize: none;
  width: 95%;
  height: calc(100vh - 40%);
  align-self: center;
  margin-top: 5px;
  margin-bottom: 5px;
}

</style>
