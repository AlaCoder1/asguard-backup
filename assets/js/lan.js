import Vue from 'vue';
import vuetify from '@/plugins/vuetify';
import 'vuetify/dist/vuetify.min.css';
import App from '@/pages/lan';
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

Vue.use( {
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
    IPV4Config: '',
    interfaces: '',
    allStaticGateways: '',
  },
  beforeMount: function () {
    this.IPV4Config = this.$el.attributes['IPV4Config'] ? this.$el.attributes['IPV4Config'].value : '';
    this.interfaces = this.$el.attributes['interfaces'] ? this.$el.attributes['interfaces'].value : '';
    this.allStaticGateways = this.$el.attributes['allStaticGateways'] ? this.$el.attributes['allStaticGateways'].value : '';
  },
  render: (h) => h(App),
}).$mount('#app');
