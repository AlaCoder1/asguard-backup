import Vue from 'vue';
import vuetify from '@/plugins/vuetify';
import App from '@/pages/test';

// any CSS you import will output into a single css file (app.css in this case)
console.log("dddd");
new Vue({
    vuetify,
    data: {
        tab: '',

    },
    beforeMount: function() {
        this.tab= this.$el.attributes['data-tab'].value;
    },
    render: (h) => h(App),
}).$mount('#app');
