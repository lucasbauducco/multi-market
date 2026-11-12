// store/index.js
import { createStore } from 'vuex';

export default createStore({
  state: {
    token: localStorage.getItem('token') || null,
    // Inicializa username desde Local Storage o usa un valor predeterminado
    username: localStorage.getItem('username') || '',
  },
  getters: {
    isLoggedIn: state => !!state.token,
  },
  mutations: {
    SET_TOKEN(state, token) {
      state.token = token;
    },
    SET_USERNAME(state, username) {
      state.username = username;
    },
    CLEAR_TOKEN(state) {
      state.token = null;
      state.username = null;
    }
  },
  actions: {
    setToken({ commit }, token) {
      localStorage.setItem('token', token);
      commit('SET_TOKEN', token);
    },
    setUserName({commit}, username){
      localStorage.setItem('username', username);
      commit('SET_USERNAME', username);
    },
    clearToken({ commit }) {
      localStorage.removeItem('token');
      commit('CLEAR_TOKEN');
    }
  }
});