<template>
  <article class="pcard">
    <router-link :to="`/producto/${product.id}`" class="media" :aria-label="product.name">
      <img v-if="product.image" :src="product.image" :alt="product.name" loading="lazy" />
      <div v-else class="noimg">Sin imagen</div>
      <span v-if="discounted" class="tag">{{ Math.round(product.discount) }}% OFF</span>
      <span v-if="soldOut" class="tag out">Sin stock</span>
    </router-link>
    <div class="body">
      <router-link :to="`/producto/${product.id}`" class="title">{{ product.name }}</router-link>
      <price-tag :product="product" />
      <div class="meta">
        <router-link v-if="product.shop_slug" :to="`/tienda/${product.shop_slug}`" class="shop">{{ product.shop_name }}</router-link>
        <span v-if="lowStock" class="low">¡Últimas {{ product.stock }}!</span>
      </div>
      <button class="btn btn-soft btn-sm btn-block add" :disabled="soldOut" @click="add">
        {{ soldOut ? 'Sin stock' : 'Agregar al carrito' }}
      </button>
    </div>
  </article>
</template>

<script>
import PriceTag from './PriceTag.vue';
import { finalPrice, hasDiscount } from '@/utils';

export default {
  name: 'ProductCard',
  components: { PriceTag },
  props: { product: { type: Object, required: true } },
  computed: {
    discounted() { return hasDiscount(this.product); },
    soldOut() { return this.product.stock === 0; },
    lowStock() { return this.product.stock !== null && this.product.stock > 0 && this.product.stock <= 3; },
  },
  methods: {
    add() {
      const p = this.product;
      this.$store.dispatch('addToCart', {
        id: p.id, name: p.name, price: finalPrice(p), image: p.image, shop: p.shop,
        shop_name: p.shop_name, shop_slug: p.shop_slug, stock: p.stock, quantity: 1,
      });
      this.$store.commit('OPEN_DRAWER');
    },
  },
};
</script>

<style scoped>
.pcard { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; display: flex; flex-direction: column; transition: box-shadow .18s, transform .18s; height: 100%; }
.pcard:hover { box-shadow: var(--shadow); transform: translateY(-2px); }
.media { position: relative; display: block; aspect-ratio: 4 / 3; background: #eef0f7; }
.media img { width: 100%; height: 100%; object-fit: cover; }
.noimg { height: 100%; display: grid; place-items: center; color: var(--muted); font-size: .85rem; }
.tag { position: absolute; top: 10px; left: 10px; background: var(--ok); color: #fff; font-weight: 700; font-size: .75rem; padding: 3px 9px; border-radius: 999px; }
.tag.out { left: auto; right: 10px; background: #374151; }
.body { padding: 12px 14px 14px; display: flex; flex-direction: column; gap: 6px; flex: 1; }
.title { color: var(--text); font-weight: 600; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 2.6em; }
.title:hover { text-decoration: none; color: var(--brand-700); }
.meta { display: flex; justify-content: space-between; gap: 8px; font-size: .8rem; color: var(--muted); }
.shop { color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.low { color: var(--warn); font-weight: 600; white-space: nowrap; }
.add { margin-top: auto; }
</style>
