import Vue from 'vue';
import VueRouter from 'vue-router';
import FirewallComponent from '../components/firewall/FirewallComponent.vue';
import IfNameComponent from '../components/network/IfNameComponent.vue'
import HomeComponent from '../pages/home.vue';

Vue.use(VueRouter);

const routes = [
  { path: '/firewall/rules', component: FirewallComponent },
  { path: '/interfaces/list-of-interface', component: IfNameComponent },
  { path: '/dashboard', component: HomeComponent },
];

const router = new VueRouter({
  mode: 'history', // Use history mode for cleaner URLs
  routes,
});

export default router;
