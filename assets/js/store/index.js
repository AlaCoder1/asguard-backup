import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

// Define your state
const state = {
  isModalOpen: false,
};

// Create the store
const store = new Vuex.Store({
  state,
});

export default store;