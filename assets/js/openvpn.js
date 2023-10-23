// import Vue from 'vue';
// import vuetify from '@/plugins/vuetify';
// import 'vuetify/dist/vuetify.min.css'
// import App from '@/pages/openvpn';
// import store from '@/store/index';


// // import VeeValidate from 'vee-validate';
// import VueI18n from 'vue-i18n';
// import dictionnary from './dictionnary';
// import enJson from './translations/en.json'; 
// import frJson from './translations/fr.json'; 

// Vue.use(VueI18n);

// const i18n = new VueI18n({
//   locale: 'en',
//   messages: {
//     en: enJson, 
//     fr: frJson, 
//   },
// });

// Vue.use( {
//   i18n,
//   classes: true,
//   fieldsBagName: 'formFields',
//   dictionary: {
//     en: {
//       messages: enJson.messages,
//       attributes: dictionnary,
//     },
//     fr: {
//       messages: frJson.messages,
//       attributes: dictionnary,
//     },
//   },
// });

// new Vue({
//   vuetify,
//   store,
//     i18n,
//     data: {},
//     render: (h) => h(App),
// }).$mount('#app');
import {createApp } from 'vue';
import store from '@/store/index.js'
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import openvpn from '@/pages/openvpn';

const app = createApp(openvpn);
const vuetify = createVuetify({
    components,
    directives
  })

app
.use(store)
.use(vuetify)
.mount('#app');