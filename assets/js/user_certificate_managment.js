import Vue from 'vue';
import vuetify from '@/plugins/vuetify';
import App from '@/pages/user_certificate_managment';

// any CSS you import will output into a single css file (app.css in this case)
import VueI18n from 'vue-i18n';
import dictionnary from './dictionnary';
import enJson from './translations/en.json';
import frJson from './translations/fr.json';
import store from '@/store/index';

Vue.use(VueI18n);

const i18n = new VueI18n({
  locale: 'en',
  messages: {
    en: enJson,
    fr: frJson,
  },
});

Vue.use({
  i18n,
  store,
  classes: true,
  fieldsBagName: 'formFields',
  dictionary: {
    en: {
      messages: enJson.messages,
      attributes: dictionnary,
    },
    fr: {
      messages: frJson.messages,
      attributes: dictionnary,
    },
  },
});


new Vue({
  vuetify,
  i18n,
  data: {
    users: '', // Pass the users data from Django
    groups: '', // Pass the groups data from Django
    servers: '', // Pass the servers data from Django

  },
 
  beforeMount: function () {
    // this.tab= this.$el.attributes['users'] ? this.$el.attributes['users'].value : '';

    console.log('Users:', this.$el.attributes['users']);
    console.log('Groups:', this.$el.attributes['groups']);
    console.log('Servers:', this.$el.attributes['servers']);

    this.users = this.$el.attributes['users'].value;
    this.groups = this.$el.attributes['groups'].value;
    this.servers = this.$el.attributes['servers'].value;


    // this.groups = this.$el.getAttribute('groups');
    // this.servers = this.$el.attributes['groups'].value;

    // console.log("users aa " + JSON.stringify(this.$el.attributes['users'].value));

    // console.log("users: " + this.users);
    // console.log("groups: " + this.groups);

  },
  // render: (h) => h(App, { props: { users_data: this.tab } }),
  render: (h) => h(App),
}).$mount('#app');
