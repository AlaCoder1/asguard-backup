import axios from 'axios';

const state = {
    user: null,
    isAuthenticated: false,
    csrfToken: null,
    messageStore:null
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
    SET_MESSAGE(state,data){
        state.messageStore = data

    },

    SET_CSRF_TOKEN(state, token) {
        state.csrfToken = token;
    }
};

const actions = {
    async login({ commit }, user) {
        try {
            const response = await axios.post('/auth/authentification', user);
            console.log(response.data);
            commit('SET_USER', response.data);
     
                let message = 'You are successfully logged in'
                commit('SET_MESSAGE',  message);
                setTimeout(()=>{
                    let message =null
                    commit('SET_MESSAGE',  message);
                },1000)
          
            window.location.href = '/dashboard';

        } catch (error) {
        
                let message = 'Invalid credentiels'
                commit('SET_MESSAGE',  message);
                setTimeout(()=>{
                    let message = null
                    commit('SET_MESSAGE',  message);
                },1000)
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
    },
    
    async fetchCsrfToken({ commit }) {
        try {
            function getCsrfToken() {
                return new Promise((resolve) => {
                    let cookieValue = null;
                    if (document.cookie && document.cookie !== '') {
                        const cookies = document.cookie.split(';');
                        for (let i = 0; i < cookies.length; i++) {
                            const cookie = cookies[i].trim();
                            if (cookie.substring(0, 'csrftoken'.length + 1) === 'csrftoken=') {
                                cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                                break;
                            }
                        }
                    }
                    resolve(cookieValue);
                });
            }
            const token = await getCsrfToken();
            commit('SET_CSRF_TOKEN', token);
        } catch (error) {
            console.error('Failed to fetch CSRF token', error);
        }
    },

};

const getters = {
    isAuthenticated(state) {
        return !!state.user;
    },
    csrfToken(state) {
        return state.csrfToken;
    }
};

export default {
    state,
    mutations,
    actions,
    getters,
};
