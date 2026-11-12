<template>
  <section class="orders">
    <h2>Pedidos recibidos</h2>
    <div class="filters">
      <button v-for="f in filters" :key="f.value" :class="{ active: filter === f.value }" @click="filter = f.value; load()">
        {{ f.label }}
      </button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="!orders.length && !error">No hay pedidos.</p>
    <article v-for="o in orders" :key="o.id" class="order">
      <header>
        <strong>#{{ o.id }}</strong> · {{ new Date(o.created_at).toLocaleString() }}
        <span class="badge" :class="o.status">{{ label(o.status) }}</span>
      </header>
      <p>
        <strong>{{ o.buyer_name }}</strong> ·
        <a :href="`https://wa.me/${o.buyer_phone.replace(/\D/g, '')}`" target="_blank" rel="noopener">{{ o.buyer_phone }}</a>
        <span v-if="o.buyer_email"> · {{ o.buyer_email }}</span>
      </p>
      <ul><li v-for="(i, idx) in o.items" :key="idx">{{ i.quantity }} × {{ i.name }} — ${{ i.subtotal }}</li></ul>
      <p v-if="o.notes" class="muted">Nota: {{ o.notes }}</p>
      <p><strong>Total ${{ o.total }}</strong></p>
      <div class="actions">
        <button v-if="o.status === 'pending'" @click="setStatus(o, 'confirmed')">Confirmar</button>
        <button v-if="o.status === 'confirmed'" @click="setStatus(o, 'delivered')">Marcar entregado</button>
        <button v-if="o.status === 'pending' || o.status === 'confirmed'" class="danger" @click="setStatus(o, 'cancelled')">Cancelar</button>
      </div>
    </article>
  </section>
</template>

<script>
import api, { errorMessage } from '@/api';

const LABELS = { pending: 'Pendiente', confirmed: 'Confirmado', delivered: 'Entregado', cancelled: 'Cancelado' };

export default {
  name: 'ShopOrders',
  data() {
    return {
      orders: [],
      filter: '',
      error: '',
      filters: [{ value: '', label: 'Todos' }, { value: 'pending', label: 'Pendientes' },
                { value: 'confirmed', label: 'Confirmados' }, { value: 'delivered', label: 'Entregados' }],
    };
  },
  methods: {
    label: s => LABELS[s] || s,
    async load() {
      this.error = '';
      try {
        const { data } = await api.get('/api/orders/', { params: this.filter ? { status: this.filter } : {} });
        this.orders = data;
      } catch (e) {
        this.error = errorMessage(e, 'No pudimos cargar los pedidos.');
      }
    },
    async setStatus(order, status) {
      if (status === 'cancelled' && !confirm('¿Cancelar el pedido? Se devuelve el stock.')) return;
      try {
        await api.patch(`/api/orders/${order.id}/status/`, { status });
        await this.load();
      } catch (e) {
        this.error = errorMessage(e);
      }
    },
  },
  mounted() { this.load(); },
};
</script>

<style scoped>
.orders { max-width: 800px; margin: 1rem auto; padding: 0 1rem; }
.filters { display: flex; gap: .5rem; margin-bottom: 1rem; flex-wrap: wrap; }
.filters .active { font-weight: bold; text-decoration: underline; }
.order { border: 1px solid #ddd; border-radius: 8px; padding: .8rem 1rem; margin-bottom: 1rem; }
.badge { margin-left: .5rem; padding: .1rem .5rem; border-radius: 10px; background: #eee; font-size: .8rem; }
.badge.pending { background: #fff3cd; } .badge.confirmed { background: #cfe2ff; }
.badge.delivered { background: #d1e7dd; } .badge.cancelled { background: #f8d7da; }
.actions { display: flex; gap: .5rem; }
.danger { color: #b00020; }
.muted { color: #666; } .error { color: #b00020; }
</style>
