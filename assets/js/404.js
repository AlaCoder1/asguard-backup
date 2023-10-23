// import Vue from 'vue';
// import vuetify from '@/plugins/vuetify';
// import App from '@/pages/404';
// import store from '@/store/index';

// // any CSS you import will output into a single css file (app.css in this case)
// new Vue({
//     vuetify,
//     store,
//     render: (h) => h(App),
// }).$mount('#app');

import {createApp } from 'vue';
import store from '@/store/index.js'
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import error from '@/pages/404';

const app = createApp(error);
const vuetify = createVuetify({
    components,
    directives
  })

app
.use(store)
.use(vuetify)
.mount('#app');