import Vue from 'vue';
import Vuex from 'vuex';
import auth from './modules/auth';
import createPersistedState from 'vuex-persistedstate';

Vue.use(Vuex);
Vue.config.devtools = true

// Create the store
const store = new Vuex.Store({
  modules: {
    auth: {
      namespaced: true,
      state: auth.state,
      mutations: auth.mutations,
      actions: auth.actions,
      getters: auth.getters,
    }
  },
  plugins: [
    // Create persisted state
    createPersistedState(),
  ],
});

export default store;