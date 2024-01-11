import {createApp } from 'vue';
import store from '../store/index.js'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import mitt from 'mitt'
import openvpn from '../views/openVpn/openvpn';
import ClientsOpenvpnComponent from '../views/openVpn/components/ClientsOpenvpnComponent.vue'
import axios from 'axios'


const emitter = mitt()

const app = createApp(openvpn);

app.component('ClientsOpenvpnComponent', ClientsOpenvpnComponent)
app.provide('emitter', emitter)


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

const currentPath = window.location.pathname;
function hrefPath(){
  localStorage.setItem('href-path', currentPath)
}

hrefPath()
const vuetify = createVuetify({
    components,
    directives
  })

app
.use(store)
.use(vuetify)
.mount('#app');