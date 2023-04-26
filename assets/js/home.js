import Vue from 'vue';
import vuetify from '@/plugins/vuetify';
import App from '@/pages/home';

// any CSS you import will output into a single css file (app.css in this case)
new Vue({
    vuetify,
    data: {
        tab: '',
    },
    beforeMount: function() {
        console.log(this);
        this.tab= this.$el.attributes['users'] ? this.$el.attributes['users'].value : '';
    },
    render: (h) => h(App),
}).$mount('#app');
