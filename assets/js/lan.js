import Vue from 'vue';
import vuetify from '@/plugins/vuetify';
import 'vuetify/dist/vuetify.min.css'
import App from '@/pages/lan';

new Vue({
    vuetify,
    data: {
        lan: '',
    },
    beforeMount: function () {
        console.log(this);
        this.lan = this.$el.attributes['lan'] ? this.$el.attributes['lan'].value : '';
    },
    render: (h) => h(App),
}).$mount('#app');
