import Vue from 'vue';
import vuetify from '@/plugins/vuetify';
import 'vuetify/dist/vuetify.min.css';
import App from '@/pages/firewall';
import VueI18n from 'vue-i18n';
import enJson from './translations/en.json';
import frJson from './translations/fr.json';
import store from '@/store/index';

Vue.use(VueI18n);

const i18n = new VueI18n({
  locale: 'en',
  messages: {
    en: enJson,
    fr: frJson,
  },
});

Vue.use({
  i18n,
  classes: true,
  fieldsBagName: 'formFields',
  dictionary: {
    en: {
      messages: enJson.messages,
    },
    fr: {
      messages: frJson.messages,
    },
  },
});

new Vue({
  i18n,
  store,
  vuetify,
  data: {
    rules: {},
    interfaces: []
  },
  beforeMount: function () {
    this.rules = this.$el.attributes['rules'] ? this.$el.attributes['rules'].value : '';
    this.interfaces = this.$el.attributes['interfaces'] ? this.$el.attributes['interfaces'].value : '';
  },
  render: (h) => h(App),
}).$mount('#app');

