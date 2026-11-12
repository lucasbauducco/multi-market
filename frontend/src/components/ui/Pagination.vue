<template>
  <nav v-if="pages > 1" class="pager" aria-label="Paginación">
    <button class="btn btn-ghost btn-sm" :disabled="current <= 1" @click="$emit('change', current - 1)">‹ Anterior</button>
    <button v-for="p in visible" :key="p" class="btn btn-sm" :class="p === current ? '' : 'btn-ghost'"
            :aria-current="p === current ? 'page' : null" @click="$emit('change', p)">{{ p }}</button>
    <button class="btn btn-ghost btn-sm" :disabled="current >= pages" @click="$emit('change', current + 1)">Siguiente ›</button>
  </nav>
</template>

<script>
export default {
  name: 'PagerNav',
  props: { current: Number, pages: Number },
  emits: ['change'],
  computed: {
    visible() {
      const out = [];
      const from = Math.max(1, this.current - 2);
      const to = Math.min(this.pages, this.current + 2);
      for (let p = from; p <= to; p++) out.push(p);
      return out;
    },
  },
};
</script>

<style scoped>
.pager { display: flex; gap: 6px; justify-content: center; margin: 28px 0 0; flex-wrap: wrap; }
</style>
