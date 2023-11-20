import {createApp } from 'vue';
import store from '../store/index.js'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import ipsec from '../views/ipsec/index.vue';

const app = createApp(ipsec);
const vuetify = createVuetify({
    components,
    directives
  })

app
.use(store)
.use(vuetify)
.mount('#app');
