import axios from 'axios';

const state = {
    user: null,
    isAuthenticated: false,
};

const mutations = {
    SET_USER(state, user) {
        state.user = user;
        state.isAuthenticated = true;
    },

    SET_LOGGED_OUT(state) {
        state.loggedIn = false;
        state.user = null;
    },
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

    async logout({ commit }) {
        try {
            await axios.get('/auth/logout');
            commit('SET_LOGGED_OUT');
            window.location.href = '/';

        } catch (error) {
            console.error('Error during logout:', error);
        }
    }

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
