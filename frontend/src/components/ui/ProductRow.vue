<template>
  <section v-if="loading || products.length" class="section">
    <div class="section-head">
      <h2>{{ title }}</h2>
      <router-link v-if="to" :to="to" class="small">Ver todo →</router-link>
    </div>
    <div class="wrap">
      <button class="arrow left" aria-label="Anterior" @click="scroll(-1)">‹</button>
      <div ref="scroller" class="scroller">
        <template v-if="loading">
          <div v-for="n in 6" :key="n" class="item"><div class="skeleton sk"></div></div>
        </template>
        <template v-else>
          <div v-for="p in products" :key="p.id" class="item"><product-card :product="p" /></div>
        </template>
      </div>
      <button class="arrow right" aria-label="Siguiente" @click="scroll(1)">›</button>
    </div>
  </section>
</template>

<script>
import ProductCard from './ProductCard.vue';

export default {
  name: 'ProductRow',
  components: { ProductCard },
  props: { title: String, products: { type: Array, default: () => [] }, to: [String, Object], loading: Boolean },
  methods: {
    scroll(dir) {
      const el = this.$refs.scroller;
      el.scrollBy({ left: dir * el.clientWidth * 0.85, behavior: 'smooth' });
    },
  },
};
</script>

<style scoped>
.wrap { position: relative; }
.scroller { display: flex; gap: 16px; overflow-x: auto; scroll-snap-type: x mandatory; padding: 4px 2px 12px; scrollbar-width: thin; }
.item { flex: 0 0 224px; scroll-snap-align: start; }
.sk { height: 340px; }
.arrow { position: absolute; top: 40%; z-index: 2; width: 38px; height: 38px; border-radius: 50%; border: 1px solid var(--border); background: #fff; box-shadow: var(--shadow); font-size: 1.4rem; line-height: 1; cursor: pointer; }
.arrow:hover { background: var(--brand-50); }
.left { left: -14px; }
.right { right: -14px; }
@media (max-width: 720px) { .arrow { display: none; } .item { flex-basis: 170px; } }
</style>
