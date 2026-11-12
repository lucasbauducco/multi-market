<template>
  <div class="stack">
    <h1>Pedidos</h1>
    <div class="row filters">
      <button v-for="f in filters" :key="f.value" class="btn btn-sm" :class="filter === f.value ? '' : 'btn-ghost'" @click="filter = f.value; load()">{{ f.label }}</button>
    </div>
    <p v-if="error" class="alert alert-bad">{{ error }}</p>
    <div v-if="loading" class="skeleton" style="height: 200px"></div>
    <empty-state v-else-if="!orders.length" icon="🧾" title="No hay pedidos" text="Cuando alguien compre en tu tienda lo vas a ver acá." />

    <article v-for="o in orders" :key="o.id" class="card card-pad order">
      <header class="row">
        <strong>Pedido #{{ o.id }}</strong>
        <span class="muted small">{{ dateTime(o.created_at) }}</span>
        <span class="spacer"></span>
        <status-badge :value="o.status" /><status-badge kind="payment" :value="o.payment_status" />
      </header>
      <div class="cols">
        <div>
          <div><strong>{{ o.buyer_name }}</strong></div>
          <div class="small"><a v-if="wa(o)" :href="wa(o)" target="_blank" rel="noopener noreferrer">💬 {{ o.buyer_phone }}</a><span v-else>{{ o.buyer_phone }}</span><span v-if="o.buyer_email"> · {{ o.buyer_email }}</span></div>
          <div class="small muted">{{ DELIVERY[o.delivery_method] }}<span v-if="o.shipping_address"> · {{ o.shipping_address }}</span></div>
          <div v-if="o.notes" class="small note">“{{ o.notes }}”</div>
        </div>
        <ul class="items"><li v-for="(i, idx) in o.items" :key="idx"><span>{{ i.quantity }} × {{ i.name }}</span><span>{{ money(i.subtotal) }}</span></li></ul>
      </div>
      <div class="row foot">
        <span class="badge badge-neutral">{{ PAYMENT_METHOD[o.payment_method] }}</span>
        <a v-if="o.proof_url" :href="o.proof_url" target="_blank" rel="noopener noreferrer" class="small">Ver comprobante</a>
        <strong class="total">{{ money(o.total, true) }}</strong>
        <span class="spacer"></span>
        <template v-if="o.payment_method !== 'mercadopago' && o.status !== 'cancelled'">
          <button v-if="o.payment_status !== 'paid'" class="btn btn-soft btn-sm" @click="setPayment(o, 'paid')">Marcar como pagado</button>
          <button v-else class="btn btn-ghost btn-sm" @click="setPayment(o, 'unpaid')">Marcar sin pagar</button>
        </template>
        <button v-if="o.status === 'pending'" class="btn btn-sm" @click="setStatus(o, 'confirmed')">Confirmar</button>
        <button v-if="o.status === 'confirmed'" class="btn btn-sm" @click="setStatus(o, 'delivered')">Marcar entregado</button>
        <button v-if="o.status === 'pending' || o.status === 'confirmed'" class="btn btn-danger btn-sm" @click="setStatus(o, 'cancelled')">Cancelar</button>
      </div>
    </article>
  </div>
</template>

<script>
import api, { errorMessage } from '@/api';
import EmptyState from '@/components/ui/EmptyState.vue';
import StatusBadge from '@/components/ui/StatusBadge.vue';
import { DELIVERY, PAYMENT_METHOD, dateTime, money, whatsappLink } from '@/utils';

export default {
  name: 'OrdersView',
  components: { EmptyState, StatusBadge },
  data() {
    return {
      orders: [], filter: '', loading: true, error: '', DELIVERY, PAYMENT_METHOD,
      filters: [{ value: '', label: 'Todos' }, { value: 'pending', label: 'Pendientes' }, { value: 'confirmed', label: 'Confirmados' }, { value: 'delivered', label: 'Entregados' }, { value: 'cancelled', label: 'Cancelados' }],
    };
  },
  methods: {
    money, dateTime,
    wa(o) { return whatsappLink(o.buyer_phone, `Hola ${o.buyer_name}! Te escribo por tu pedido #${o.id} de Multi-Market.`); },
    async load() {
      this.error = '';
      try { this.orders = (await api.get('/api/orders/', { params: this.filter ? { status: this.filter } : {} })).data; } catch (e) { this.error = errorMessage(e); } finally { this.loading = false; }
    },
    async setStatus(o, status) {
      if (status === 'cancelled' && !confirm('¿Cancelar el pedido? Se devuelve el stock.')) return;
      try { await api.patch(`/api/orders/${o.id}/status/`, { status }); await this.load(); } catch (e) { this.error = errorMessage(e); }
    },
    async setPayment(o, payment_status) {
      try { await api.patch(`/api/orders/${o.id}/payment/`, { payment_status }); await this.load(); } catch (e) { this.error = errorMessage(e); }
    },
  },
  mounted() { document.title = 'Pedidos – Multi-Market'; this.load(); },
};
</script>

<style scoped>
.order { display: flex; flex-direction: column; gap: 12px; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.items { list-style: none; margin: 0; padding: 0; }
.items li { display: flex; justify-content: space-between; gap: 10px; padding: 3px 0; }
.note { color: #4b5563; margin-top: 4px; }
.foot { border-top: 1px solid var(--border); padding-top: 12px; }
.total { font-size: 1.1rem; }
@media (max-width: 760px) { .cols { grid-template-columns: 1fr; } }
</style>
