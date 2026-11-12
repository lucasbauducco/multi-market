<template>
  <div class="container page">
    <breadcrumbs :items="crumbs" />
    <div class="layout">
      <!-- Filtros -->
      <aside class="filters card card-pad" :class="{ open: showFilters }" aria-label="Filtros">
        <div class="f-head">
          <h3>Filtros</h3>
          <button v-if="activeFilters" class="btn-link small" @click="clearAll">Limpiar</button>
        </div>

        <div class="f-block">
          <div class="label">Categoría</div>
          <ul class="f-list">
            <li><a href="#" :class="{ on: !f.category }" @click.prevent="setFilter({ category: undefined })">Todas</a></li>
            <li v-for="c in categories" :key="c.id">
              <a href="#" :class="{ on: String(f.category) === String(c.id) }" @click.prevent="setFilter({ category: c.id })">{{ c.name }}</a>
            </li>
          </ul>
        </div>

        <div class="f-block">
          <div class="label">Precio</div>
          <form class="price-form" @submit.prevent="applyPrice">
            <input v-model="minPrice" class="input" type="number" min="0" placeholder="Mín." aria-label="Precio mínimo" />
            <span>–</span>
            <input v-model="maxPrice" class="input" type="number" min="0" placeholder="Máx." aria-label="Precio máximo" />
            <button class="btn btn-soft btn-sm" type="submit">OK</button>
          </form>
        </div>

        <div class="f-block">
          <div class="label">Tienda</div>
          <select class="input" :value="f.shop || ''" @change="setFilter({ shop: $event.target.value || undefined })">
            <option value="">Todas</option>
            <option v-for="s in shops" :key="s.id" :value="s.id">{{ s.razon_social }}</option>
          </select>
        </div>

        <div class="f-block">
          <label class="checkbox"><input type="checkbox" :checked="f.discounted === '1'" @change="setFilter({ discounted: $event.target.checked ? '1' : undefined })" /> Solo con descuento</label>
          <label class="checkbox"><input type="checkbox" :checked="f.in_stock === '1'" @change="setFilter({ in_stock: $event.target.checked ? '1' : undefined })" /> Solo con stock</label>
        </div>
      </aside>

      <!-- Resultados -->
      <section class="results">
        <div class="bar">
          <div>
            <h1>{{ title }}</h1>
            <span class="muted small" v-if="!loading">{{ total }} resultado{{ total === 1 ? '' : 's' }}</span>
          </div>
          <div class="row">
            <button class="btn btn-ghost btn-sm filter-toggle" @click="showFilters = !showFilters">Filtros{{ activeFilters ? ` (${activeFilters})` : '' }}</button>
            <label class="visually-hidden" for="ord">Ordenar</label>
            <select id="ord" class="input ord" :value="f.ordering || 'relevance'" @change="setFilter({ ordering: $event.target.value })">
              <option value="relevance">Más relevantes</option>
              <option value="price_asc">Menor precio</option>
              <option value="price_desc">Mayor precio</option>
              <option value="discount">Mayor descuento</option>
              <option value="newest">Más nuevos</option>
            </select>
          </div>
        </div>

        <div v-if="chips.length" class="chips">
          <button v-for="c in chips" :key="c.key" class="chip" @click="setFilter({ [c.key]: undefined })">{{ c.label }} ✕</button>
        </div>

        <div v-if="loading" class="product-grid">
          <div v-for="n in 8" :key="n" class="skeleton sk"></div>
        </div>
        <empty-state v-else-if="!products.length" icon="🔎" title="No encontramos resultados"
                     text="Probá con otras palabras o quitá algunos filtros.">
          <button class="btn" @click="clearAll">Quitar filtros</button>
        </empty-state>
        <div v-else class="product-grid">
          <product-card v-for="p in products" :key="p.id" :product="p" />
        </div>

        <pagination :current="current" :pages="pages" @change="goPage" />
      </section>
    </div>
  </div>
</template>

<script>
import api from '@/api';
import Breadcrumbs from '@/components/ui/Breadcrumbs.vue';
import ProductCard from '@/components/ui/ProductCard.vue';
import Pagination from '@/components/ui/Pagination.vue';
import EmptyState from '@/components/ui/EmptyState.vue';
import { money } from '@/utils';

const KEYS = ['query', 'category', 'shop', 'min_price', 'max_price', 'discounted', 'in_stock', 'ordering', 'page'];

export default {
  name: 'SearchView',
  components: { Breadcrumbs, ProductCard, Pagination, EmptyState },
  data() {
    return { loading: true, products: [], total: 0, pages: 1, current: 1, categories: [], shops: [], showFilters: false, minPrice: '', maxPrice: '' };
  },
  computed: {
    f() { return this.$route.query; },
    categoryName() {
      const c = this.categories.find(x => String(x.id) === String(this.f.category));
      return c ? c.name : '';
    },
    title() {
      if (this.f.query) return `Resultados para “${this.f.query}”`;
      if (this.categoryName) return this.categoryName;
      if (this.f.discounted === '1') return 'Ofertas';
      return 'Todos los productos';
    },
    crumbs() {
      const out = [{ label: 'Inicio', to: '/' }, { label: 'Productos', to: this.categoryName || this.f.query ? '/buscar' : null }];
      if (this.categoryName) out.push({ label: this.categoryName });
      else if (this.f.query) out.push({ label: this.f.query });
      return out;
    },
    activeFilters() {
      return ['category', 'shop', 'min_price', 'max_price', 'discounted', 'in_stock'].filter(k => this.f[k]).length;
    },
    chips() {
      const out = [];
      if (this.f.query) out.push({ key: 'query', label: `“${this.f.query}”` });
      if (this.f.category && this.categoryName) out.push({ key: 'category', label: this.categoryName });
      const shop = this.shops.find(s => String(s.id) === String(this.f.shop));
      if (shop) out.push({ key: 'shop', label: shop.razon_social });
      if (this.f.min_price) out.push({ key: 'min_price', label: `Desde ${money(this.f.min_price)}` });
      if (this.f.max_price) out.push({ key: 'max_price', label: `Hasta ${money(this.f.max_price)}` });
      if (this.f.discounted === '1') out.push({ key: 'discounted', label: 'Con descuento' });
      if (this.f.in_stock === '1') out.push({ key: 'in_stock', label: 'Con stock' });
      return out;
    },
  },
  watch: {
    '$route.query': { handler() { this.syncPrice(); this.load(); }, deep: true },
  },
  methods: {
    syncPrice() { this.minPrice = this.f.min_price || ''; this.maxPrice = this.f.max_price || ''; },
    setFilter(patch) {
      const q = { ...this.f, ...patch, page: undefined };
      Object.keys(q).forEach(k => { if (q[k] === undefined || q[k] === '') delete q[k]; });
      this.$router.push({ path: '/buscar', query: q });
    },
    applyPrice() { this.setFilter({ min_price: this.minPrice || undefined, max_price: this.maxPrice || undefined }); },
    clearAll() { this.$router.push({ path: '/buscar' }); },
    goPage(p) {
      this.$router.push({ path: '/buscar', query: { ...this.f, page: p } });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    async load() {
      this.loading = true;
      const params = {};
      KEYS.forEach((k) => { if (this.f[k]) params[k] = this.f[k]; });
      try {
        const { data } = await api.get('/api/search_products/', { params });
        this.products = data.products;
        this.total = data.total;
        this.pages = data.pages;
        this.current = data.current;
      } catch (e) {
        this.products = [];
        this.total = 0;
      } finally {
        this.loading = false;
        this.showFilters = false;
      }
      document.title = `${this.title} – Multi-Market`;
    },
  },
  async mounted() {
    this.syncPrice();
    this.load();
    try {
      const [cats, shops] = await Promise.all([api.get('/api/categories/categories-with-products/'), api.get('/api/shops/')]);
      this.categories = cats.data.map(c => ({ id: c.id, name: c.name }));
      this.shops = shops.data;
    } catch (e) { /* los filtros funcionan sin las listas */ }
  },
};
</script>

<style scoped>
.layout { display: grid; grid-template-columns: 250px 1fr; gap: 22px; align-items: start; }
.filters { position: sticky; top: 130px; }
.f-head { display: flex; justify-content: space-between; align-items: center; }
.f-head h3 { margin: 0; }
.f-block { margin-top: 18px; display: flex; flex-direction: column; gap: 8px; }
.f-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 2px; }
.f-list a { display: block; padding: 5px 8px; border-radius: 8px; color: #374151; }
.f-list a:hover { background: var(--brand-50); text-decoration: none; }
.f-list a.on { background: var(--brand-50); color: var(--brand-700); font-weight: 700; }
.price-form { display: flex; align-items: center; gap: 6px; }
.price-form .input { padding: 7px 8px; }
.bar { display: flex; justify-content: space-between; align-items: flex-end; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.bar h1 { margin: 0; font-size: 1.4rem; }
.ord { width: auto; padding: 8px 10px; }
.filter-toggle { display: none; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
.chip { border: 1px solid var(--border); background: #fff; border-radius: 999px; padding: 4px 12px; font-size: .82rem; cursor: pointer; }
.chip:hover { background: var(--brand-50); }
.sk { height: 340px; }
@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
  .filters { display: none; position: static; }
  .filters.open { display: block; }
  .filter-toggle { display: inline-flex; }
}
</style>
