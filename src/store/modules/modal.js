export default {
    state: {
      isModalOpen: false,
    },
    mutations: {
      openModal(state) {
        state.isModalOpen = true;
      },
      closeModal(state) {
        state.isModalOpen = false;
      },
    },
    actions: {
      openModal({ commit }) {
        commit('openModal');
      },
      closeModal({ commit }) {
        commit('closeModal');
      },
    },
  };