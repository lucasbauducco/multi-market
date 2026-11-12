<template>
  <header class="hdr">
    <div class="topbar">
      <div class="container topbar-in">
        <span>🔒 Pagos seguros · 🏪 Tiendas verificadas · 💬 Atención directa con cada tienda</span>
        <router-link v-if="!isLoggedIn" to="/registro">Vendé en Multi-Market</router-link>
        <router-link v-else to="/panel">Ir a mi panel</router-link>
      </div>
    </div>

    <div class="container main">
      <button class="burger" aria-label="Menú" :aria-expanded="menu" @click="menu = !menu">☰</button>
      <brand-logo />

      <form class="search" role="search" @submit.prevent="search">
        <label class="visually-hidden" for="q">Buscar productos</label>
        <input id="q" v-model.trim="q" class="input" type="search" placeholder="Buscar productos, marcas y tiendas…" autocomplete="off" />
        <button class="btn" type="submit" aria-label="Buscar">
          <svg width="18" height="18" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001q.044.06.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1 1 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0"/></svg>
        </button>
      </form>

      <nav class="actions" aria-label="Cuenta">
        <router-link v-if="!isLoggedIn" to="/ingresar" class="act">
          <span class="ico">👤</span><span class="lbl">Ingresar</span>
        </router-link>
        <router-link v-else to="/panel" class="act">
          <span class="ico">🏪</span><span class="lbl">{{ razonSocial || 'Mi tienda' }}</span>
        </router-link>
        <button class="act cart" @click="$store.commit('OPEN_DRAWER')" :aria-label="`Carrito, ${cartCount} productos`">
          <span class="ico">🛒</span><span class="lbl">Carrito</span>
          <span v-if="cartCount" class="count">{{ cartCount }}</span>
        </button>
      </nav>
    </div>

    <nav class="cats" :class="{ open: menu }" aria-label="Categorías">
      <div class="container cats-in">
        <router-link to="/buscar?discounted=1&ordering=discount" class="hot" @click="menu = false">🔥 Ofertas</router-link>
        <router-link v-for="c in categories" :key="c.id" :to="`/buscar?category=${c.id}`" @click="menu = false">{{ c.name }}</router-link>
        <router-link to="/tiendas" @click="menu = false">Tiendas</router-link>
        <router-link to="/ayuda" class="right" @click="menu = false">Ayuda</router-link>
      </div>
    </nav>
  </header>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import api from '@/api';
import BrandLogo from './BrandLogo.vue';

export default {
  name: 'AppHeader',
  components: { BrandLogo },
  data() { return { q: this.$route.query.query || '', categories: [], menu: false }; },
  computed: {
    ...mapGetters(['cartCount', 'isLoggedIn']),
    ...mapState(['razonSocial']),
  },
  watch: {
    '$route.query.query'(v) { this.q = v || ''; },
  },
  methods: {
    search() {
      this.$router.push({ path: '/buscar', query: this.q ? { query: this.q } : {} });
    },
  },
  async mounted() {
    try {
      const { data } = await api.get('/api/categories/categories-with-products/');
      this.categories = data.map(c => ({ id: c.id, name: c.name }));
    } catch (e) { /* la barra funciona sin categorías */ }
  },
};
</script>

<style scoped>
.hdr { background: var(--surface); position: sticky; top: 0; z-index: 40; box-shadow: var(--shadow-sm); }
.topbar { background: var(--brand-900); color: #c7d2fe; font-size: .78rem; }
.topbar-in { display: flex; justify-content: space-between; gap: 12px; padding-top: 6px; padding-bottom: 6px; }
.topbar a { color: #fff; font-weight: 600; white-space: nowrap; }
.main { display: flex; align-items: center; gap: 18px; padding-top: 12px; padding-bottom: 12px; }
.burger { display: none; background: none; border: 0; font-size: 1.5rem; cursor: pointer; }
.search { flex: 1; display: flex; max-width: 720px; }
.search .input { border-radius: 10px 0 0 10px; }
.search .btn { border-radius: 0 10px 10px 0; padding: 0 16px; }
.actions { display: flex; gap: 6px; margin-left: auto; }
.act { position: relative; display: flex; align-items: center; gap: 6px; padding: 8px 10px; border-radius: 10px; color: var(--text); font-weight: 600; background: none; border: 0; font: inherit; cursor: pointer; text-decoration: none !important; }
.act:hover { background: var(--brand-50); }
.ico { font-size: 1.25rem; }
.count { position: absolute; top: 0; left: 24px; background: var(--accent); color: #2b1a00; font-size: .7rem; font-weight: 800; border-radius: 999px; padding: 0 6px; min-width: 18px; text-align: center; }
.cats { border-top: 1px solid var(--border); background: #fafbff; }
.cats-in { display: flex; gap: 4px; overflow-x: auto; scrollbar-width: none; }
.cats a { padding: 10px 14px; color: #374151; font-weight: 600; font-size: .9rem; white-space: nowrap; border-bottom: 3px solid transparent; }
.cats a:hover { text-decoration: none; color: var(--brand-700); border-bottom-color: var(--brand-500); }
.cats a.hot { color: var(--bad); }
.cats a.right { margin-left: auto; }
@media (max-width: 820px) {
  .topbar span { display: none; }
  .topbar-in { justify-content: flex-end; }
  .main { flex-wrap: wrap; gap: 8px 10px; }
  .burger { display: block; }
  .search { order: 5; flex-basis: 100%; max-width: none; }
  .actions { margin-left: auto; }
  .lbl { display: none; }
  .cats { display: none; }
  .cats.open { display: block; }
  .cats-in { flex-direction: column; }
}
</style>
