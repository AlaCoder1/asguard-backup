import axios from 'axios';

const state = {
    user: null,
    isAuthenticated: false,
};

const mutations = {
    SET_USER(state, user) {
        state.user = user;
    },

    CLEAR_USER(state) {
        state.user = null;
    }
};

const actions = {
    async login({ commit }, user) {
        try {
            const response = await axios.post('/auth/authentification', user);
            console.log(response.data);
            commit('SET_USER', response.data);
            window.location.href = '/dashboard';

        } catch (error) {
            console.error('Error during login:', error);
        }
    },

    logout({ commit }) {
        // Perform logout logic (e.g., clear local storage) and then commit mutation
        commit('CLEAR_USER');
    },
};

const getters = {
    isAuthenticated(state) {
        return !!state.user;
    }
};

export default {
    state,
    mutations,
    actions,
    getters,
};
