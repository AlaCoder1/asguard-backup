import {createApp } from 'vue';
import store from '../store/index.js'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import ipsec from '../views/ipsec/index.vue';
import axios from 'axios'
import mitt from 'mitt'

const emitter = mitt()

const app = createApp(ipsec);

app.provide('emitter', emitter)


const vuetify = createVuetify({
    components,
    directives
  })

 
  axios.interceptors.response.use(
    (response) => {
      return response;
    },
    (error) => {
      console.log('errorMainipsec',error)
      if ((error.response.status === 401 )||(error.response.status === 403)) {
        console.log('Token expired or unauthorized. Redirecting to login.');
        window.location.href = '/';
      }
      return Promise.reject(error);
    }
  );

app
.use(store)
.use(vuetify)
.mount('#app');
