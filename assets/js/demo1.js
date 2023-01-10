import Vue from 'vue';
import vuetify from '@/plugins/vuetify';
import App from '@/pages/home';

// any CSS you import will output into a single css file (app.css in this case)
console.log("wselt");
new Vue({
    vuetify,
    render: (h) => h(App),
}).$mount('#app');
