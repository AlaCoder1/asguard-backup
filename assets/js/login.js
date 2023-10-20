// import Vue from 'vue';
// import vuetify from '@/plugins/vuetify';
// import App from '@/pages/login';
// import store from '@/store/index';

// // any CSS you import will output into a single css file (app.css in this case)
// new Vue({
//     vuetify,
//     store,
//     data: {
//         tab: '',
//     },
//     beforeMount: function() {
//         console.log(this);
//         this.tab= this.$el.attributes['users'] ? this.$el.attributes['users'].value : '';
//     },
//     render: (h) => h(App),
// }).$mount('#app');

import { compile, createApp } from 'vue';
import error from '@/pages/404';
// const app = createApp({
//     // data(){
//     //     return{
//     //         firstname:'souhail'
//     //     }
//     // },
//     // template:`<h1>hello souhail </h1>`,
//     render(h){
//         return h(error)
//     }


// }).mount('#app')
// let test = this.$el.attributes['users'] ? this.$el.attributes['users'].value : '';
// console.log('test',test)
const app = createApp(error);
app.mount('#app');