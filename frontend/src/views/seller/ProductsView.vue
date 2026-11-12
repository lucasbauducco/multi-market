<template>
  <div class="stack">
    <div class="row">
      <h1>Productos</h1>
      <span class="spacer"></span>
      <router-link to="/panel/productos/nuevo" class="btn">+ Nuevo producto</router-link>
    </div>
    <p v-if="error" class="alert alert-bad">{{ error }}</p>
    <div v-if="loading" class="skeleton" style="height: 240px"></div>
    <empty-state v-else-if="!products.length" icon="📦" title="Todavía no cargaste productos" text="Publicá tu primer producto para empezar a vender." to="/panel/productos/nuevo" cta="Crear producto" />

    <div v-else class="card tbl">
      <table class="table">
        <thead><tr><th>Producto</th><th>Precio</th><th>Stock</th><th>Estado</th><th></th></tr></thead>
        <tbody>
          <tr v-for="p in products" :key="p.id">
            <td>
              <div class="prod">
                <img v-if="p.image" :src="p.image" alt="" /><div v-else class="ph"></div>
                <div><strong>{{ p.name }}</strong><div class="small muted">{{ p.category_name || 'Sin categoría' }}</div></div>
              </div>
            </td>
            <td>
              <div>{{ money(p.final_price) }}</div>
              <div v-if="p.discount > 0" class="small muted"><s>{{ money(p.price) }}</s> · {{ Math.round(p.discount) }}% OFF</div>
            </td>
            <td><span :class="{ 'badge badge-bad': p.stock === 0, 'badge badge-warn': p.stock > 0 && p.stock <= 3 }">{{ p.stock === null ? '∞' : p.stock }}</span></td>
            <td><button class="badge as-btn" :class="p.state === 'active' ? 'badge-ok' : 'badge-neutral'" @click="toggle(p)">{{ p.state === 'active' ? 'Activo' : 'Pausado' }}</button></td>
            <td class="acts">
              <router-link :to="`/producto/${p.id}`" class="btn btn-ghost btn-sm">Ver</router-link>
              <router-link :to="`/panel/productos/${p.id}`" class="btn btn-soft btn-sm">Editar</router-link>
              <button class="btn btn-danger btn-sm" @click="remove(p)">Borrar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api, { errorMessage } from '@/api';
import EmptyState from '@/components/ui/EmptyState.vue';
import { money } from '@/utils';

export default {
  name: 'ProductsView',
  components: { EmptyState },
  data() { return { products: [], loading: true, error: '' }; },
  methods: {
    money,
    async load() {
      try { const { data } = await api.get('/api/products/'); this.products = data.results || data; } catch (e) { this.error = errorMessage(e); } finally { this.loading = false; }
    },
    async toggle(p) {
      const state = p.state === 'active' ? 'inactive' : 'active';
      try { await api.patch(`/api/products/${p.id}/`, { state }); p.state = state; } catch (e) { this.error = errorMessage(e); }
    },
    async remove(p) {
      if (!confirm(`¿Borrar "${p.name}"? Esta acción no se puede deshacer.`)) return;
      try { await api.delete(`/api/products/delete/${p.id}/`); this.products = this.products.filter(x => x.id !== p.id); } catch (e) { this.error = errorMessage(e); }
    },
  },
  mounted() { document.title = 'Productos – Multi-Market'; this.load(); },
};
</script>

<style scoped>
.tbl { overflow-x: auto; }
.prod { display: flex; align-items: center; gap: 12px; min-width: 220px; }
.prod img, .ph { width: 52px; height: 52px; border-radius: 10px; object-fit: cover; background: #eef0f7; flex: 0 0 auto; }
.acts { display: flex; gap: 6px; justify-content: flex-end; }
.as-btn { border: 0; cursor: pointer; font: inherit; font-size: .75rem; font-weight: 700; }
</style>
