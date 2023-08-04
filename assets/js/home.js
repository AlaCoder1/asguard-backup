import Vue from 'vue';
import vuetify from '@/plugins/vuetify';
import App from '@/pages/home';
import store from './store'; // Adjust the path to your store.js file

// any CSS you import will output into a single css file (app.css in this case)


new Vue({
    store,
    vuetify,

    data: {
        tab: '',
    },
    beforeMount: function () {
        // this.tab= this.$el.attributes['users'] ? this.$el.attributes['users'].value : '';
        this.tab = this.$el.attributes['users'].value;
   
        console.log("users object " + JSON.stringify(this.$el.attributes['users'].value));


    },
    // render: (h) => h(App, { props: { users_data: this.tab } }),
    render: (h) => h(App),
}).$mount('#app');
