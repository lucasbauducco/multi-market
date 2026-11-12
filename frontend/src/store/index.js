// store/index.js
import { createStore } from 'vuex';

const CART_KEY = 'cart';

function loadCart() {
  try {
    return JSON.parse(localStorage.getItem(CART_KEY)) || [];
  } catch (e) {
    return [];
  }
}

function saveCart(items) {
  try {
    localStorage.setItem(CART_KEY, JSON.stringify(items));
  } catch (e) { /* almacenamiento no disponible */ }
}

export default createStore({
  state: {
    token: localStorage.getItem('token') || null,
    username: localStorage.getItem('username') || '',
    // items: { id, name, price (precio final unitario), image, shop_name, quantity }
    cart: loadCart(),
  },
  getters: {
    isLoggedIn: state => !!state.token,
    cartCount: state => state.cart.reduce((n, i) => n + i.quantity, 0),
    cartTotal: state => state.cart.reduce((t, i) => t + i.price * i.quantity, 0),
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
      state.username = '';
    },
    ADD_TO_CART(state, item) {
      const found = state.cart.find(i => i.id === item.id);
      if (found) found.quantity += item.quantity;
      else state.cart.push({ ...item });
      saveCart(state.cart);
    },
    SET_QUANTITY(state, { id, quantity }) {
      const found = state.cart.find(i => i.id === id);
      if (found) found.quantity = Math.max(1, Math.min(999, quantity));
      saveCart(state.cart);
    },
    REMOVE_FROM_CART(state, id) {
      state.cart = state.cart.filter(i => i.id !== id);
      saveCart(state.cart);
    },
    CLEAR_CART(state) {
      state.cart = [];
      saveCart(state.cart);
    },
  },
  actions: {
    setToken({ commit }, token) {
      localStorage.setItem('token', token);
      commit('SET_TOKEN', token);
    },
    setUserName({ commit }, username) {
      localStorage.setItem('username', username);
      commit('SET_USERNAME', username);
    },
    clearToken({ commit }) {
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      commit('CLEAR_TOKEN');
    },
    addToCart({ commit }, item) { commit('ADD_TO_CART', { quantity: 1, ...item }); },
    setQuantity({ commit }, payload) { commit('SET_QUANTITY', payload); },
    removeFromCart({ commit }, id) { commit('REMOVE_FROM_CART', id); },
    clearCart({ commit }) { commit('CLEAR_CART'); },
  },
});
