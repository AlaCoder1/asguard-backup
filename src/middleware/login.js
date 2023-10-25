import {createApp } from 'vue';
import vuetify from '@/plugins/vuetify';
import store from '../store/index.js'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import login from '../views/auth/login.vue';

const app = createApp(login);
const vuetifyComponents = createVuetify({
    components,
    directives
  })

app
.use(store)
.use(vuetifyComponents)
.use(vuetify)
.mount('#app');
