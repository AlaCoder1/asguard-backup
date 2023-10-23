// import Vue from 'vue';
// import vuetify from '@/plugins/vuetify';
// import App from '@/pages/home';
// import store from '@/store/index';
// import VueRouter from 'vue-router';
// import router from './routes/router';
// import VueCompositionAPI from '@vue/composition-api'





// import VueI18n from 'vue-i18n';
// import enJson from './translations/en.json'; 
// import frJson from './translations/fr.json'; 

// Vue.use(VueI18n);
// Vue.use(VueRouter);
// Vue.use(VueCompositionAPI)


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
//     },
//     fr: {
//       messages: frJson.messages,
//     },
//   },
// });

// new Vue({
//     store,
//     i18n,
//     vuetify,
//     router,
//     data: {
//         tab: '',
//         gateways:null,
//         interfaces: null,
        
//     },
//     beforeMount: function () {
//         this.tab = this.$el.attributes['informations'].value;
//         this.gateways = this.$el.attributes['gateways'].value;
//         this.interfaces = this.$el.attributes['interfaces'] ? this.$el.attributes['interfaces'].value : '';
//     },
//     render: (h) => h(App),
// }).$mount('#app');

import {createApp } from 'vue';
import store from '@/store/index.js'
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import home from '@/pages/home';

const app = createApp(home);
const vuetify = createVuetify({
    components,
    directives
  })

app
.use(store)
.use(vuetify)
.mount('#app');