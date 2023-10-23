// import Vue from 'vue';
// import vuetify from '@/plugins/vuetify';
// import 'vuetify/dist/vuetify.min.css';


// import App from '@/pages/UserAndCertificateManagement';

// import VueI18n from 'vue-i18n';
// import enJson from './translations/en.json';
// import frJson from './translations/fr.json';
// import store from '@/store/index';
// import { ValidationProvider } from 'vee-validate/dist/vee-validate.full.esm';
// import { ValidationObserver } from 'vee-validate';

// Vue.use(VueI18n);
// Vue.component('ValidationProvider', ValidationProvider);
// Vue.component('ValidationObserver', ValidationObserver);

// const i18n = new VueI18n({
//   locale: 'en',
//   messages: {
//     en: enJson,
//     fr: frJson,
//   },
// });

// Vue.use({

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
//   store,
//   vuetify,
//   i18n,
//   data: {
//     users: '',
//     groups: '',
//     servers: '', // Pass the servers data from Django

//   },
//   beforeMount: function () {
//     console.log('Users:', this.$el.attributes['users']);
//     console.log('Groups:', this.$el.attributes['groups']);
//     console.log('Servers:', this.$el.attributes['servers']);

//     this.users = this.$el.attributes['users'].value;
//     this.groups = this.$el.attributes['groups'].value;
//     this.servers = this.$el.attributes['servers'].value;
//   },
//   render: (h) => h(App),
// }).$mount('#app');
import {createApp } from 'vue';
import store from '@/store/index.js'
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import UserManagement from '@/pages/UserAndCertificateManagement';

const app = createApp(UserManagement);
const vuetify = createVuetify({
    components,
    directives
  })

app
.use(store)
.use(vuetify)
.mount('#app');