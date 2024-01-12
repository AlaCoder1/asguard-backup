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
import axios from 'axios'
import {createApp } from 'vue';
import store from '../store/index.js'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import success from '../views/success.vue';

const app = createApp(success);
const vuetify = createVuetify({
    components,
    directives
  })

  axios.interceptors.response.use(
    (response) => {
      return response;
    },
    (error) => {    
      if ((error.response.status === 401 )||(error.response.status === 403)) {
        window.location.href = '/';
      }
      return Promise.reject(error);
    }
  );
 

app
.use(store)
.use(vuetify)
.mount('#app');