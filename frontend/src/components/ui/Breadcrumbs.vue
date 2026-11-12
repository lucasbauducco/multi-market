<template>
  <nav class="crumbs" aria-label="Migas de pan">
    <template v-for="(c, i) in items" :key="i">
      <router-link v-if="c.to" :to="c.to">{{ c.label }}</router-link>
      <span v-else aria-current="page">{{ c.label }}</span>
      <span v-if="i < items.length - 1" class="sep" aria-hidden="true">›</span>
    </template>
  </nav>
</template>

<script>
export default { name: 'BreadCrumbs', props: { items: { type: Array, default: () => [] } } };
</script>

<style scoped>
.crumbs { font-size: .85rem; color: var(--muted); margin-bottom: 14px; display: flex; flex-wrap: wrap; gap: 6px; }
.crumbs a { color: var(--muted); }
.crumbs a:hover { color: var(--brand-600); }
.crumbs span[aria-current] { color: var(--text); font-weight: 600; }
</style>
