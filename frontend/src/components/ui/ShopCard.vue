<template>
  <router-link :to="`/tienda/${shop.slug}`" class="shopcard card">
    <div class="cover" :style="shop.banner ? { backgroundImage: `url(${shop.banner})` } : {}"></div>
    <div class="logo">
      <img v-if="shop.logo" :src="shop.logo" :alt="shop.razon_social" loading="lazy" />
      <span v-else>{{ shop.razon_social.slice(0, 1) }}</span>
    </div>
    <div class="info">
      <strong>{{ shop.razon_social }}</strong>
      <span class="muted small">{{ shop.product_count }} productos</span>
    </div>
  </router-link>
</template>

<script>
export default { name: 'ShopCard', props: { shop: { type: Object, required: true } } };
</script>

<style scoped>
.shopcard { display: block; overflow: hidden; color: var(--text); transition: box-shadow .18s, transform .18s; position: relative; }
.shopcard:hover { text-decoration: none; box-shadow: var(--shadow); transform: translateY(-2px); }
.cover { height: 78px; background: linear-gradient(135deg, var(--brand-500), #7c3aed); background-size: cover; background-position: center; }
.logo { position: absolute; top: 44px; left: 14px; width: 56px; height: 56px; border-radius: 14px; background: #fff; border: 3px solid #fff; box-shadow: var(--shadow-sm); overflow: hidden; display: grid; place-items: center; font-weight: 800; color: var(--brand-600); font-size: 1.4rem; }
.logo img { width: 100%; height: 100%; object-fit: cover; }
.info { padding: 34px 14px 14px; display: flex; flex-direction: column; }
</style>
