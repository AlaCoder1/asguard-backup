import Vue from 'vue';
import vuetify from '@/plugins/vuetify';
import App from '@/pages/404';
import store from '@/store/index';

// any CSS you import will output into a single css file (app.css in this case)
new Vue({
    vuetify,
    store,
    render: (h) => h(App),
}).$mount('#app');
