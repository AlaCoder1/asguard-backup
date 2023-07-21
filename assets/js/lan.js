import Vue from 'vue';
import vuetify from '@/plugins/vuetify';
import 'vuetify/dist/vuetify.min.css'
import App from '@/pages/lan';

new Vue({
    vuetify,
    data: {},
    render: (h) => h(App),
}).$mount('#app');
