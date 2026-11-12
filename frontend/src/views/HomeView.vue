<template>
  <div class="container page">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-text">
        <span class="kicker">Marketplace de tiendas</span>
        <h1>Todas las tiendas,<br />un solo carrito.</h1>
        <p>Compará ofertas de comercios verificados, pagá como prefieras y coordiná la entrega directo con cada tienda.</p>
        <div class="row">
          <router-link to="/buscar?discounted=1&ordering=discount" class="btn btn-accent btn-lg">Ver ofertas</router-link>
          <router-link to="/registro" class="btn btn-lg hero-ghost">Quiero vender</router-link>
        </div>
      </div>
      <div class="hero-art" aria-hidden="true">
        <div v-for="(p, i) in heroProducts" :key="p.id" class="art" :class="`a${i}`">
          <img :src="p.image" alt="" loading="eager" />
        </div>
      </div>
    </section>

    <!-- Confianza -->
    <section class="trust">
      <div v-for="t in trust" :key="t.title" class="card trust-item">
        <span class="t-ico">{{ t.icon }}</span>
        <div><strong>{{ t.title }}</strong><div class="muted small">{{ t.text }}</div></div>
      </div>
    </section>

    <!-- Categorías -->
    <section v-if="data.categories.length" class="section">
      <div class="section-head"><h2>Comprá por categoría</h2></div>
      <div class="cat-grid">
        <router-link v-for="c in data.categories" :key="c.id" :to="`/buscar?category=${c.id}`" class="cat card">
          <img v-if="cover(c)" :src="cover(c)" alt="" loading="lazy" />
          <div class="cat-name"><strong>{{ c.name }}</strong><span class="small">{{ c.count }} productos</span></div>
        </router-link>
      </div>
    </section>

    <product-row title="🔥 Ofertas del día" :products="data.deals" :loading="loading" to="/buscar?discounted=1&ordering=discount" />

    <section v-if="data.shops.length" class="section">
      <div class="section-head"><h2>Tiendas destacadas</h2><router-link to="/tiendas" class="small">Ver todas →</router-link></div>
      <div class="shop-grid"><shop-card v-for="s in data.shops" :key="s.id" :shop="s" /></div>
    </section>

    <product-row v-for="c in data.categories" :key="c.id" :title="c.name" :products="c.products" :to="`/buscar?category=${c.id}`" />

    <product-row title="Recién llegados" :products="data.newest" :loading="loading" to="/buscar?ordering=newest" />

    <empty-state v-if="!loading && !data.deals.length && !data.newest.length" title="Todavía no hay productos"
                 text="Las tiendas están cargando su catálogo. ¡Volvé en un rato!" />
  </div>
</template>

<script>
import api from '@/api';
import ProductRow from '@/components/ui/ProductRow.vue';
import ShopCard from '@/components/ui/ShopCard.vue';
import EmptyState from '@/components/ui/EmptyState.vue';

export default {
  name: 'HomeView',
  components: { ProductRow, ShopCard, EmptyState },
  data() {
    return {
      loading: true,
      data: { deals: [], newest: [], categories: [], shops: [] },
      trust: [
        { icon: '🔒', title: 'Pago seguro', text: 'Mercado Pago, transferencia o efectivo' },
        { icon: '🏪', title: 'Tiendas verificadas', text: 'Cada comercio es revisado' },
        { icon: '💬', title: 'Atención directa', text: 'Hablás con la tienda por WhatsApp' },
        { icon: '📦', title: 'Un pedido por tienda', text: 'Seguimiento sin crear cuenta' },
      ],
    };
  },
  computed: {
    heroProducts() {
      return [...this.data.deals, ...this.data.newest].filter(p => p.image).slice(0, 3);
    },
  },
  methods: {
    // Imagen de portada de la categoría: el producto con mayor descuento que tenga foto.
    cover(c) {
      const withImg = c.products.filter(p => p.image).sort((x, y) => Number(y.discount) - Number(x.discount));
      return withImg.length ? withImg[0].image : null;
    },
  },
  async mounted() {
    document.title = 'Multi-Market – Marketplace de tiendas';
    try {
      this.data = (await api.get('/api/home/')).data;
    } catch (e) { /* se muestra el estado vacío */ } finally { this.loading = false; }
  },
};
</script>

<style scoped>
.hero { display: grid; grid-template-columns: 1.1fr .9fr; gap: 24px; align-items: center; border-radius: 22px; padding: 44px 48px; color: #fff; overflow: hidden; position: relative;
  background: radial-gradient(1200px 400px at 85% -10%, #8b5cf6 0%, transparent 60%), linear-gradient(120deg, #3730a3, #4f46e5 55%, #6d28d9); }
.kicker { text-transform: uppercase; letter-spacing: .12em; font-size: .75rem; font-weight: 700; color: #c7d2fe; }
.hero h1 { font-size: 2.7rem; margin: 8px 0 12px; line-height: 1.08; }
.hero p { color: #e0e7ff; font-size: 1.05rem; max-width: 480px; margin-bottom: 22px; }
.hero-ghost { background: rgba(255, 255, 255, .14); }
.hero-ghost:hover { background: rgba(255, 255, 255, .25); }
.hero-art { position: relative; height: 270px; }
.art { position: absolute; width: 190px; height: 190px; border-radius: 20px; overflow: hidden; box-shadow: 0 18px 40px rgba(10, 8, 50, .45); border: 4px solid rgba(255, 255, 255, .85); background: #fff; }
.art img { width: 100%; height: 100%; object-fit: cover; }
.a0 { left: 6%; top: 8%; transform: rotate(-6deg); }
.a1 { left: 38%; top: 0; transform: rotate(4deg); z-index: 2; width: 210px; height: 210px; }
.a2 { left: 56%; top: 46%; transform: rotate(-3deg); z-index: 3; }
.trust { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 16px; }
.trust-item { display: flex; align-items: center; gap: 12px; padding: 14px 16px; }
.t-ico { font-size: 1.6rem; }
.cat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 14px; }
.cat { position: relative; display: block; height: 130px; overflow: hidden; color: #fff; }
.cat:hover { text-decoration: none; box-shadow: var(--shadow); }
.cat img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transition: transform .3s; }
.cat:hover img { transform: scale(1.06); }
.cat::after { content: ''; position: absolute; inset: 0; background: linear-gradient(0deg, rgba(20, 16, 70, .82), rgba(20, 16, 70, .1) 70%); }
.cat-name { position: absolute; z-index: 2; left: 14px; bottom: 12px; display: flex; flex-direction: column; }
.shop-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 14px; }
@media (max-width: 900px) {
  .hero { grid-template-columns: 1fr; padding: 28px 22px; }
  .hero h1 { font-size: 2rem; }
  .hero-art { display: none; }
  .trust { grid-template-columns: 1fr 1fr; }
}
</style>
