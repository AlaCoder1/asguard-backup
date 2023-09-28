import VueRouter from 'vue-router';
import FirewallComponent from '../components/firewall/FirewallComponent.vue';
import HomeComponent from '../pages/home.vue';


const routes = [
  { path: '/firewall/rules', component: FirewallComponent },
  { path: '/dashboard', component: HomeComponent }

];

const router = new VueRouter({
  mode: 'history', // Use history mode for cleaner URLs
  routes,
});

export default router;
