import Vue from 'vue';
import vuetify from '@/plugins/vuetify';
import App from '@/pages/home';

// any CSS you import will output into a single css file (app.css in this case)
new Vue({
    vuetify,
    el: '#app',
    data: {
        tab: '',
    },
    beforeMount: function() {
        this.tab= this.$el.attributes['users'].value;
    },
    render: (h) => h(App),
}).$mount('#app');
