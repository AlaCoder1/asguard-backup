import Vue from 'vue';
import VueRouter from 'vue-router';  
import FirewallComponent from '../components/firewall/FirewallComponent.vue';  
import IfNameComponent from '../components/network/IfNameComponent.vue';  
import HomeComponent from '../pages/home.vue'; 
import BackupComponent from '../views/backup/index.vue';  
Vue.use(VueRouter);

const routes = [
  { path: '/firewall/rules', component: FirewallComponent },
  { path: '/interfaces/list-of-interface', component: IfNameComponent },
  { path: '/dashboard', component: HomeComponent },
  { path: '/backup', component: BackupComponent },
];

const router = new VueRouter({
  mode: 'history',
  base: '/asguard/',
  routes,
});

export default router;
