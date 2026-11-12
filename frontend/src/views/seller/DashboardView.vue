<template>
  <div class="stack">
    <h1>Resumen</h1>
    <div v-if="loading" class="kpis"><div v-for="n in 4" :key="n" class="skeleton" style="height: 96px"></div></div>
    <template v-else-if="d">
      <div class="kpis">
        <div class="card card-pad kpi"><span class="muted small">Ventas cobradas</span><strong>{{ money(d.sales_paid) }}</strong></div>
        <div class="card card-pad kpi"><span class="muted small">Por cobrar</span><strong>{{ money(d.sales_pending_payment) }}</strong></div>
        <div class="card card-pad kpi"><span class="muted small">Pedidos pendientes</span><strong>{{ d.orders_pending }}</strong></div>
        <div class="card card-pad kpi"><span class="muted small">Productos activos</span><strong>{{ d.products_active }}<small> / {{ d.products_total }}</small></strong></div>
      </div>

      <div v-if="!hasMethods" class="alert alert-warn">
        Todavía no configuraste cómo cobrar con Mercado Pago, transferencia u otros medios.
        <router-link to="/panel/configuracion">Configurar cobros →</router-link>
      </div>

      <div class="cols">
        <section class="card card-pad">
          <div class="section-head"><h2>Últimos pedidos</h2><router-link to="/panel/pedidos" class="small">Ver todos</router-link></div>
          <p v-if="!d.recent_orders.length" class="muted">Aún no recibiste pedidos.</p>
          <div v-for="o in d.recent_orders" :key="o.id" class="orow">
            <div><strong>#{{ o.id }}</strong> {{ o.buyer_name }}<div class="small muted">{{ dateTime(o.created_at) }}</div></div>
            <div class="r"><strong>{{ money(o.total) }}</strong><div><status-badge :value="o.status" /> <status-badge kind="payment" :value="o.payment_status" /></div></div>
          </div>
        </section>
        <section class="card card-pad">
          <div class="section-head"><h2>Stock bajo</h2><router-link to="/panel/productos" class="small">Productos</router-link></div>
          <p v-if="!d.low_stock.length" class="muted">Todo en orden 👌</p>
          <div v-for="p in d.low_stock" :key="p.id" class="orow">
            <router-link :to="`/panel/productos/${p.id}`">{{ p.name }}</router-link>
            <span class="badge" :class="p.stock === 0 ? 'badge-bad' : 'badge-warn'">{{ p.stock === 0 ? 'Sin stock' : `${p.stock} u.` }}</span>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<script>
import api from '@/api';
import StatusBadge from '@/components/ui/StatusBadge.vue';
import { dateTime, money } from '@/utils';

export default {
  name: 'DashboardView',
  components: { StatusBadge },
  data() { return { d: null, loading: true, hasMethods: true }; },
  methods: { money, dateTime },
  async mounted() {
    document.title = 'Panel – Multi-Market';
    try {
      const [d, ps] = await Promise.all([api.get('/api/shop/dashboard/'), api.get('/api/shop/payment-settings/')]);
      this.d = d.data;
      const s = ps.data;
      this.hasMethods = s.mp_connected || s.accepts_transfer || s.accepts_link;
    } catch (e) { /* vacío */ } finally { this.loading = false; }
  },
};
</script>

<style scoped>
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; }
.kpi { display: flex; flex-direction: column; gap: 4px; }
.kpi strong { font-size: 1.7rem; letter-spacing: -.02em; }
.kpi small { color: var(--muted); font-weight: 500; font-size: 1rem; }
.cols { display: grid; grid-template-columns: 1.4fr 1fr; gap: 14px; }
.orow { display: flex; justify-content: space-between; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border); align-items: center; }
.orow:last-child { border-bottom: 0; }
.r { text-align: right; }
@media (max-width: 900px) { .cols { grid-template-columns: 1fr; } }
</style>
