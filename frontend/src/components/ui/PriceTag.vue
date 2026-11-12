<template>
  <div class="price" :class="{ big }">
    <div v-if="discounted" class="old">{{ money(product.price) }}</div>
    <div class="now-row">
      <span class="now">{{ money(final) }}</span>
      <span v-if="discounted" class="off">{{ Math.round(product.discount) }}% OFF</span>
    </div>
  </div>
</template>

<script>
import { finalPrice, hasDiscount, money } from '@/utils';

export default {
  name: 'PriceTag',
  props: { product: { type: Object, required: true }, big: Boolean },
  computed: {
    final() { return finalPrice(this.product); },
    discounted() { return hasDiscount(this.product); },
  },
  methods: { money },
};
</script>

<style scoped>
.old { color: var(--muted); text-decoration: line-through; font-size: .85rem; }
.now-row { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
.now { font-size: 1.35rem; font-weight: 800; letter-spacing: -.02em; }
.off { color: var(--ok); font-weight: 700; font-size: .85rem; }
.big .now { font-size: 2.1rem; }
.big .old { font-size: 1rem; }
.big .off { font-size: 1rem; }
</style>
