import {createApp } from 'vue';
import store from '../store/index.js'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import mitt from 'mitt'
import IdsIps from '../views/ids_ips/IdsIps';

const emitter = mitt()

const app = createApp(IdsIps);

app.provide('emitter', emitter)

const vuetify = createVuetify({
    components,
    directives
  })

app
.use(store)
.use(vuetify)
.mount('#app');