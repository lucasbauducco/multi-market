<template>
  <router-link to="/" class="logo" :class="{ light }" :aria-label="`${brand.name} – inicio`">
    <img src="@/assets/brand/logo-mark.svg" alt="" width="38" height="38" />
    <span class="word">Multi<b>-Market</b></span>
  </router-link>
</template>

<script>
import { BRAND } from '@/brand';

export default {
  name: 'BrandLogo',
  props: { light: Boolean },
  data() { return { brand: BRAND }; },
};
</script>

<style scoped>
.logo { display: inline-flex; align-items: center; gap: 9px; color: var(--brand-900); text-decoration: none !important; }
.word { font-size: 1.35rem; font-weight: 800; letter-spacing: -.03em; }
.word b { color: var(--brand-600); font-weight: 800; }
.light { color: #fff; }
.light .word b { color: #c7d2fe; }
</style>
