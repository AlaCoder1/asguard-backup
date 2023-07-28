import Vue from 'vue';
import vuetify from '@/plugins/vuetify';
import App from '@/pages/user_certificate_managment';

// any CSS you import will output into a single css file (app.css in this case)


new Vue({
    vuetify,

    data: {
        users: '',
        groups:'',
    },
    beforeMount: function () {
        // this.tab= this.$el.attributes['users'] ? this.$el.attributes['users'].value : '';
        this.users = this.$el.attributes['users'].value;
       // this.groups = this.$el.attributes['groups'].value;
   
        console.log("users aa " + JSON.stringify(this.$el.attributes['users'].value));

    },
    // render: (h) => h(App, { props: { users_data: this.tab } }),
    render: (h) => h(App),
}).$mount('#app');
