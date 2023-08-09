import Vue from 'vue';
import vuetify from '@/plugins/vuetify';
import App from '@/pages/user_certificate_managment';

// any CSS you import will output into a single css file (app.css in this case)
import VeeValidate from 'vee-validate';
import VueI18n from 'vue-i18n';
import dictionnary from './dictionnary';
import enJson from './translations/en.json'; 
import frJson from './translations/fr.json'; 

Vue.use(VueI18n);

const i18n = new VueI18n({
  locale: 'en',
  messages: {
    en: enJson, 
    fr: frJson, 
  },
});

Vue.use(VeeValidate, {
  i18n,
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
