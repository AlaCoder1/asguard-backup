import Vue from 'vue';
import vuetify from '@/plugins/vuetify';
import App from '@/pages/home';

// any CSS you import will output into a single css file (app.css in this case)

const usersData = [
    { id: 1, name: 'John' },
    { id: 2, name: 'Alice' },
    // ... more user objects
  ];
  
new Vue({
    vuetify,

    props: {
        users: {
          type: Array,
          required: true,
        },
      },

    data: {
        tab: '',
    },
    beforeMount: function() {
        console.log(this);
        this.tab= this.$el.attributes['users'] ? this.$el.attributes['users'].value : '';
    },
    render: (h) => h(App, { props: { users_data: usersData } }),
}).$mount('#app');
