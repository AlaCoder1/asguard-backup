// store.js
import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);
Vue.config.devtools = true

const state = {
  // Your state properties go here
  count:0,
};

const mutations = {
  incrementCount(state) {
    state.count++;
  },
};

const actions = {
  // Your actions go here
};

const getters = {
  // Your getters go here
};

export default new Vuex.Store({
  state,
  mutations,
  actions,
  getters,
});