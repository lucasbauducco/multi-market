<template>
  <div class="container page">
    <div v-if="loading" class="card card-pad"><div class="skeleton" style="height: 420px"></div></div>
    <empty-state v-else-if="!product" icon="😕" title="Producto no disponible" text="Puede que la tienda lo haya pausado o eliminado." to="/buscar" cta="Ver otros productos" />

    <template v-else>
      <breadcrumbs :items="crumbs" />
      <div class="grid">
        <!-- Galería -->
        <section class="gallery card card-pad">
          <div class="main-img">
            <img v-if="current" :src="current" :alt="product.name" />
            <div v-else class="noimg">Sin imagen</div>
            <span v-if="product.discount > 0" class="badge badge-off off">{{ Math.round(product.discount) }}% OFF</span>
          </div>
          <div v-if="product.images.length > 1" class="thumbs">
            <button v-for="(img, i) in product.images" :key="i" class="thumb" :class="{ on: img === current }" :aria-label="`Imagen ${i + 1}`" @click="current = img">
              <img :src="img" alt="" loading="lazy" />
            </button>
          </div>
        </section>

        <!-- Compra -->
        <section class="buy card card-pad">
          <router-link v-if="shop" :to="`/tienda/${shop.slug}`" class="small shoplink">Vendido por <strong>{{ shop.razon_social }}</strong></router-link>
          <h1>{{ product.name }}</h1>
          <price-tag :product="product" big />
          <p class="small muted pay-note" v-if="methods.length">
            Medios de pago: <strong>{{ methods.map(m => m.label).join(' · ') }}</strong>
          </p>

          <div class="stock" :class="{ out: soldOut, low: lowStock }">
            <template v-if="soldOut">Sin stock por el momento</template>
            <template v-else-if="lowStock">¡Quedan solo {{ product.stock }} unidades!</template>
            <template v-else>Disponible</template>
          </div>

          <div class="qty-row" v-if="!soldOut">
            <label class="label" for="qty">Cantidad</label>
            <div class="qty">
              <button aria-label="Menos" :disabled="qty <= 1" @click="qty--">−</button>
              <input id="qty" v-model.number="qty" type="number" min="1" :max="max" @change="clampQty" />
              <button aria-label="Más" :disabled="qty >= max" @click="qty++">+</button>
            </div>
            <span v-if="product.stock !== null" class="muted small">({{ product.stock }} disponibles)</span>
          </div>

          <div class="cta">
            <button class="btn btn-accent btn-lg btn-block" :disabled="soldOut" @click="buyNow">Comprar ahora</button>
            <button class="btn btn-soft btn-lg btn-block" :disabled="soldOut" @click="addToCart">Agregar al carrito</button>
          </div>

          <ul class="perks">
            <li>🔒 Compra protegida: el pago se acuerda con la tienda</li>
            <li>💬 Consultá cualquier duda por WhatsApp</li>
            <li>📦 Seguimiento del pedido sin crear cuenta</li>
          </ul>

          <div v-if="shop" class="shopbox">
            <div class="logo"><img v-if="shop.logo" :src="shop.logo" alt="" /><span v-else>{{ shop.razon_social.slice(0, 1) }}</span></div>
            <div class="grow">
              <strong>{{ shop.razon_social }}</strong>
              <div class="small muted">{{ shop.product_count }} productos</div>
            </div>
            <a v-if="wa" :href="wa" target="_blank" rel="noopener" class="btn btn-ghost btn-sm">WhatsApp</a>
            <router-link :to="`/tienda/${shop.slug}`" class="btn btn-ghost btn-sm">Ver tienda</router-link>
          </div>
        </section>
      </div>

      <section class="card card-pad desc">
        <h2>Descripción</h2>
        <p class="pre">{{ product.description }}</p>
      </section>

      <product-row title="Productos relacionados" :products="related" />
      <product-row v-if="shop" :title="`Más de ${shop.razon_social}`" :products="more" :to="`/tienda/${shop.slug}`" />
    </template>
  </div>
</template>

<script>
import api from '@/api';
import Breadcrumbs from '@/components/ui/Breadcrumbs.vue';
import PriceTag from '@/components/ui/PriceTag.vue';
import ProductRow from '@/components/ui/ProductRow.vue';
import EmptyState from '@/components/ui/EmptyState.vue';
import { finalPrice, whatsappLink } from '@/utils';

export default {
  name: 'ProductView',
  components: { Breadcrumbs, PriceTag, ProductRow, EmptyState },
  data() {
    return { loading: true, product: null, shop: null, methods: [], current: null, qty: 1, related: [], more: [] };
  },
  computed: {
    soldOut() { return this.product && this.product.stock === 0; },
    lowStock() { return this.product && this.product.stock !== null && this.product.stock > 0 && this.product.stock <= 3; },
    max() { return this.product && this.product.stock !== null ? Math.max(this.product.stock, 1) : 99; },
    wa() { return this.shop ? whatsappLink(this.shop.telefono, `Hola! Me interesa "${this.product.name}" de Multi-Market.`) : null; },
    crumbs() {
      const c = [{ label: 'Inicio', to: '/' }, { label: 'Productos', to: '/buscar' }];
      if (this.product.category_name) c.push({ label: this.product.category_name, to: `/buscar?category=${this.product.category_id || ''}` });
      c.push({ label: this.product.name });
      return c;
    },
  },
  methods: {
    clampQty() { this.qty = Math.max(1, Math.min(this.max, parseInt(this.qty) || 1)); },
    cartItem() {
      const p = this.product;
      return { id: p.id, name: p.name, price: finalPrice(p), image: p.image, shop: p.shop, shop_name: p.shop_name,
        shop_slug: p.shop_slug, stock: p.stock, quantity: Math.max(1, this.qty) };
    },
    addToCart() { this.$store.dispatch('addToCart', this.cartItem()); this.$store.commit('OPEN_DRAWER'); },
    buyNow() { this.$store.dispatch('addToCart', this.cartItem()); this.$router.push('/checkout'); },
    async load() {
      try {
        const { data } = await api.get(`/api/product/${this.$route.params.id}/`);
        this.product = data;
        this.current = data.images[0] || null;
        document.title = `${data.name} – Multi-Market`;
        const [shop, methods, related, more] = await Promise.all([
          api.get(`/api/shops/${data.shop_slug}/`),
          api.get('/api/checkout/methods/', { params: { shops: data.shop } }),
          data.subcategory ? api.get('/api/search_products/', { params: { category: '', subcategory: data.subcategory, exclude: data.id, limit: 10 } }) : Promise.resolve({ data: { products: [] } }),
          api.get('/api/search_products/', { params: { shop: data.shop, exclude: data.id, limit: 10 } }),
        ]);
        this.shop = shop.data;
        this.methods = (methods.data[data.shop] || {}).methods || [];
        this.related = related.data.products;
        this.more = more.data.products;
      } catch (e) {
        if (!this.product) this.product = null;
      } finally {
        this.loading = false;
      }
    },
  },
  mounted() { this.load(); },
};
</script>

<style scoped>
.grid { display: grid; grid-template-columns: 1.15fr 1fr; gap: 20px; align-items: start; }
.main-img { position: relative; aspect-ratio: 4 / 3; border-radius: var(--radius); overflow: hidden; background: #eef0f7; }
.main-img img { width: 100%; height: 100%; object-fit: cover; }
.noimg { height: 100%; display: grid; place-items: center; color: var(--muted); }
.off { position: absolute; top: 12px; left: 12px; font-size: .9rem; padding: 4px 12px; }
.thumbs { display: flex; gap: 8px; margin-top: 10px; overflow-x: auto; }
.thumb { width: 72px; height: 72px; padding: 0; border: 2px solid transparent; border-radius: 10px; overflow: hidden; cursor: pointer; background: #eef0f7; flex: 0 0 auto; }
.thumb.on { border-color: var(--brand-600); }
.thumb img { width: 100%; height: 100%; object-fit: cover; }
.buy h1 { font-size: 1.55rem; margin: 6px 0 12px; }
.shoplink { color: var(--muted); }
.pay-note { margin: 8px 0; }
.stock { margin: 10px 0; font-weight: 600; color: var(--ok); }
.stock.low { color: var(--warn); }
.stock.out { color: var(--bad); }
.qty-row { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.qty { display: inline-flex; align-items: center; border: 1px solid #cfd3e2; border-radius: 10px; overflow: hidden; }
.qty button { width: 36px; height: 38px; border: 0; background: #f4f5fa; cursor: pointer; font-size: 1.1rem; }
.qty input { width: 54px; border: 0; text-align: center; font: inherit; font-weight: 600; -moz-appearance: textfield; }
.cta { display: grid; gap: 10px; margin-bottom: 16px; }
.perks { list-style: none; padding: 0; margin: 0 0 16px; display: grid; gap: 6px; font-size: .88rem; color: #4b5563; }
.shopbox { display: flex; align-items: center; gap: 12px; border-top: 1px solid var(--border); padding-top: 14px; flex-wrap: wrap; }
.grow { flex: 1; min-width: 120px; }
.logo { width: 46px; height: 46px; border-radius: 12px; background: var(--brand-50); color: var(--brand-600); font-weight: 800; display: grid; place-items: center; overflow: hidden; }
.logo img { width: 100%; height: 100%; object-fit: cover; }
.desc { margin-top: 20px; }
.pre { white-space: pre-line; }
@media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
</style>
