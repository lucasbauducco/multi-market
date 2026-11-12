<template>
  <div class="container page">
    <h1>Tiendas</h1>
    <p class="muted">Comercios verificados que venden en Multi-Market.</p>
    <div v-if="loading" class="grid"><div v-for="n in 6" :key="n" class="skeleton" style="height: 150px"></div></div>
    <empty-state v-else-if="!shops.length" icon="🏪" title="Aún no hay tiendas" text="¿Tenés un comercio? Sumate." to="/registro" cta="Registrar mi tienda" />
    <div v-else class="grid"><shop-card v-for="s in shops" :key="s.id" :shop="s" /></div>
  </div>
</template>

<script>
import api from '@/api';
import ShopCard from '@/components/ui/ShopCard.vue';
import EmptyState from '@/components/ui/EmptyState.vue';

export default {
  name: 'ShopsView',
  components: { ShopCard, EmptyState },
  data() { return { shops: [], loading: true }; },
  async mounted() {
    document.title = 'Tiendas – Multi-Market';
    try { this.shops = (await api.get('/api/shops/')).data; } catch (e) { /* vacío */ } finally { this.loading = false; }
  },
};
</script>

<style scoped>
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 16px; margin-top: 16px; }
</style>
