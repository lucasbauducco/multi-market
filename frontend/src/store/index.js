// store/index.js
import { createStore } from 'vuex';

const CART_KEY = 'cart';

function loadCart() {
  try {
    const items = JSON.parse(localStorage.getItem(CART_KEY)) || [];
    return Array.isArray(items) ? items : [];
  } catch (e) {
    return [];
  }
}

function saveCart(items) {
  try {
    localStorage.setItem(CART_KEY, JSON.stringify(items));
  } catch (e) { /* almacenamiento no disponible */ }
}

function clamp(item, quantity) {
  const max = item.stock !== null && item.stock !== undefined ? Math.max(item.stock, 1) : 999;
  return Math.max(1, Math.min(max, 999, quantity));
}

export default createStore({
  state: {
    token: localStorage.getItem('token') || null,
    username: localStorage.getItem('username') || '',
    razonSocial: localStorage.getItem('razon_social') || '',
    // items: { id, name, price (precio final unitario), image, shop, shop_name, shop_slug, stock, quantity }
    cart: loadCart(),
    drawerOpen: false,
  },
  getters: {
    isLoggedIn: state => !!state.token,
    cartCount: state => state.cart.reduce((n, i) => n + i.quantity, 0),
    cartTotal: state => state.cart.reduce((t, i) => t + i.price * i.quantity, 0),
    // Agrupado por tienda: cada tienda genera un pedido distinto.
    cartByShop: state => {
      const groups = {};
      state.cart.forEach((i) => {
        const key = i.shop;
        if (!groups[key]) groups[key] = { shop: i.shop, shop_name: i.shop_name, shop_slug: i.shop_slug, items: [], total: 0 };
        groups[key].items.push(i);
        groups[key].total += i.price * i.quantity;
      });
      return Object.values(groups);
    },
  },
  mutations: {
    SET_TOKEN(state, token) { state.token = token; },
    SET_USERNAME(state, username) { state.username = username; },
    SET_RAZON_SOCIAL(state, name) { state.razonSocial = name; },
    CLEAR_TOKEN(state) {
      state.token = null;
      state.username = '';
      state.razonSocial = '';
    },
    ADD_TO_CART(state, item) {
      const found = state.cart.find(i => i.id === item.id);
      if (found) {
        found.quantity = clamp(found, found.quantity + item.quantity);
        found.price = item.price;
        found.stock = item.stock;
      } else {
        state.cart.push({ ...item, quantity: clamp(item, item.quantity) });
      }
      saveCart(state.cart);
    },
    SET_QUANTITY(state, { id, quantity }) {
      const found = state.cart.find(i => i.id === id);
      if (found) found.quantity = clamp(found, quantity);
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
    REMOVE_SHOP_ITEMS(state, shopId) {
      state.cart = state.cart.filter(i => i.shop !== shopId);
      saveCart(state.cart);
    },
    OPEN_DRAWER(state) { state.drawerOpen = true; },
    CLOSE_DRAWER(state) { state.drawerOpen = false; },
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
    setRazonSocial({ commit }, name) {
      localStorage.setItem('razon_social', name || '');
      commit('SET_RAZON_SOCIAL', name || '');
    },
    clearToken({ commit }) {
      ['token', 'username', 'razon_social'].forEach(k => localStorage.removeItem(k));
      commit('CLEAR_TOKEN');
    },
    addToCart({ commit }, item) { commit('ADD_TO_CART', { quantity: 1, ...item }); },
    setQuantity({ commit }, payload) { commit('SET_QUANTITY', payload); },
    removeFromCart({ commit }, id) { commit('REMOVE_FROM_CART', id); },
    clearCart({ commit }) { commit('CLEAR_CART'); },
  },
});
