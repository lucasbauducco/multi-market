<template>
  <div class="page">
    <div v-if="loading" class="container"><div class="skeleton" style="height: 260px"></div></div>
    <div v-else-if="!shop" class="container"><empty-state icon="🏪" title="Tienda no encontrada" to="/tiendas" cta="Ver tiendas" /></div>

    <template v-else>
      <div class="cover" :style="shop.banner ? { backgroundImage: `url(${shop.banner})` } : {}"></div>
      <div class="container">
        <header class="info card card-pad">
          <div class="logo"><img v-if="shop.logo" :src="shop.logo" :alt="shop.razon_social" /><span v-else>{{ shop.razon_social.slice(0, 1) }}</span></div>
          <div class="grow">
            <h1>{{ shop.razon_social }}</h1>
            <p class="muted">{{ shop.description || 'Tienda verificada de Multi-Market.' }}</p>
            <div class="row small">
              <span class="badge badge-ok">✔ Tienda verificada</span>
              <span class="muted">{{ shop.product_count }} productos</span>
              <span v-for="m in methods" :key="m.code" class="badge badge-neutral">{{ m.label }}</span>
            </div>
          </div>
          <a v-if="wa" :href="wa" target="_blank" rel="noopener noreferrer" class="btn btn-ghost">💬 WhatsApp</a>
        </header>

        <div class="bar">
          <h2>Catálogo</h2>
          <select class="input ord" v-model="ordering" aria-label="Ordenar" @change="load(1)">
            <option value="relevance">Más relevantes</option>
            <option value="price_asc">Menor precio</option>
            <option value="price_desc">Mayor precio</option>
            <option value="discount">Mayor descuento</option>
            <option value="newest">Más nuevos</option>
          </select>
        </div>
        <div class="product-grid"><product-card v-for="p in products" :key="p.id" :product="p" /></div>
        <pagination :current="current" :pages="pages" @change="load" />
      </div>
    </template>
  </div>
</template>

<script>
import api from '@/api';
import EmptyState from '@/components/ui/EmptyState.vue';
import ProductCard from '@/components/ui/ProductCard.vue';
import Pagination from '@/components/ui/Pagination.vue';
import { whatsappLink } from '@/utils';

export default {
  name: 'ShopPageView',
  components: { EmptyState, ProductCard, Pagination },
  data() { return { loading: true, shop: null, methods: [], products: [], current: 1, pages: 1, ordering: 'relevance' }; },
  computed: {
    wa() { return this.shop ? whatsappLink(this.shop.telefono, `Hola ${this.shop.razon_social}! Te escribo desde Multi-Market.`) : null; },
  },
  methods: {
    async load(page = 1) {
      const { data } = await api.get('/api/search_products/', { params: { shop: this.shop.id, ordering: this.ordering, page, limit: 12 } });
      this.products = data.products; this.current = data.current; this.pages = data.pages;
    },
  },
  async mounted() {
    try {
      this.shop = (await api.get(`/api/shops/${this.$route.params.slug}/`)).data;
      document.title = `${this.shop.razon_social} – Multi-Market`;
      const [, methods] = await Promise.all([this.load(1), api.get('/api/checkout/methods/', { params: { shops: this.shop.id } })]);
      this.methods = (methods.data[this.shop.id] || {}).methods || [];
    } catch (e) { this.shop = null; } finally { this.loading = false; }
  },
};
</script>

<style scoped>
.cover { height: 220px; background: linear-gradient(120deg, #3730a3, #6d28d9); background-size: cover; background-position: center; }
.info { display: flex; gap: 18px; align-items: center; margin-top: -48px; position: relative; flex-wrap: wrap; }
.logo { width: 96px; height: 96px; border-radius: 20px; background: var(--brand-50); color: var(--brand-600); font-size: 2.4rem; font-weight: 800; display: grid; place-items: center; overflow: hidden; border: 4px solid #fff; box-shadow: var(--shadow); flex: 0 0 auto; }
.logo img { width: 100%; height: 100%; object-fit: cover; }
.grow { flex: 1; min-width: 220px; }
.grow h1 { margin-bottom: 4px; }
.bar { display: flex; justify-content: space-between; align-items: center; margin: 26px 0 12px; }
.bar h2 { margin: 0; }
.ord { width: auto; }
</style>
