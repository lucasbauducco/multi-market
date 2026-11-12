<template>
  <div class="container page narrow">
    <div v-if="loading" class="card card-pad"><div class="skeleton" style="height: 260px"></div></div>
    <empty-state v-else-if="!order" icon="🔍" title="No encontramos el pedido" text="Revisá que el enlace esté completo." to="/" cta="Ir al inicio" />

    <template v-else>
      <div class="head">
        <div>
          <h1>Pedido #{{ order.id }}</h1>
          <span class="muted small">{{ dateTime(order.created_at) }} · {{ order.shop_name }}</span>
        </div>
        <div class="row">
          <status-badge :value="order.status" />
          <status-badge kind="payment" :value="order.payment_status" />
          <button class="btn btn-ghost btn-sm" @click="load">Actualizar</button>
        </div>
      </div>

      <div v-if="mpReturn" class="alert" :class="mpReturn.cls">{{ mpReturn.text }}</div>

      <!-- Seguimiento -->
      <ol class="timeline card card-pad">
        <li v-for="(s, i) in timeline" :key="s.label" :class="{ on: i <= progress, bad: order.status === 'cancelled' && i === 0 }">
          <span class="dot"></span>{{ s.label }}
        </li>
      </ol>

      <!-- Pago -->
      <section v-if="order.status !== 'cancelled'" class="card card-pad pay">
        <h2>Pago</h2>
        <template v-if="order.payment_status === 'paid'">
          <p class="alert alert-ok">✅ Pago recibido. ¡Gracias!</p>
        </template>
        <template v-else-if="ins.type === 'mercadopago'">
          <p>Pagá de forma segura con tarjeta, dinero en cuenta o QR a través de Mercado Pago.</p>
          <button class="btn btn-accent btn-lg" :disabled="paying" @click="payMp">{{ paying ? 'Redirigiendo…' : `Pagar ${money(order.total)}` }}</button>
          <p v-if="payError" class="error-text">{{ payError }}</p>
        </template>
        <template v-else-if="ins.type === 'transfer'">
          <p>Transferí <strong>{{ money(order.total, true) }}</strong> con estos datos:</p>
          <dl class="kv">
            <dt v-if="ins.holder">Titular</dt><dd v-if="ins.holder">{{ ins.holder }}</dd>
            <dt v-if="ins.alias">Alias</dt><dd v-if="ins.alias">{{ ins.alias }} <button class="btn-link small" @click="copy(ins.alias)">{{ copied === ins.alias ? '¡Copiado!' : 'Copiar' }}</button></dd>
            <dt v-if="ins.cbu">CBU/CVU</dt><dd v-if="ins.cbu">{{ ins.cbu }} <button class="btn-link small" @click="copy(ins.cbu)">{{ copied === ins.cbu ? '¡Copiado!' : 'Copiar' }}</button></dd>
          </dl>
          <div v-if="order.has_proof" class="alert alert-info">Comprobante enviado. La tienda lo está revisando.</div>
          <div class="field">
            <label for="proof" class="label">{{ order.has_proof ? 'Reemplazar comprobante' : 'Subí tu comprobante' }}</label>
            <input id="proof" type="file" accept="image/*" class="input" @change="onProof" />
            <span class="hint">Imagen o captura (hasta 3 MB).</span>
          </div>
          <p v-if="proofError" class="error-text">{{ proofError }}</p>
        </template>
        <template v-else-if="ins.type === 'link'">
          <p>Abrí el link de pago de la tienda (<strong>{{ ins.label }}</strong>) y pagá <strong>{{ money(order.total, true) }}</strong>. Luego avisale por WhatsApp.</p>
          <a :href="ins.url" target="_blank" rel="noopener noreferrer" class="btn btn-lg">Abrir link de pago</a>
        </template>
        <template v-else-if="ins.type === 'cash'">
          <p>Pagás <strong>{{ money(order.total, true) }}</strong> en efectivo al {{ order.delivery_method === 'pickup' ? 'retirar' : 'recibir' }} tu pedido.</p>
          <p v-if="ins.instructions" class="alert alert-info">{{ ins.instructions }}</p>
        </template>
      </section>

      <!-- Detalle -->
      <section class="card card-pad">
        <h2>Detalle</h2>
        <div v-for="(i, idx) in order.items" :key="idx" class="item"><span>{{ i.quantity }} × {{ i.name }}</span><strong>{{ money(i.subtotal) }}</strong></div>
        <div class="item total"><span>Total</span><strong>{{ money(order.total, true) }}</strong></div>
        <p class="small muted">{{ DELIVERY[order.delivery_method] }}<span v-if="order.shipping_address"> · {{ order.shipping_address }}</span> · {{ PAYMENT_METHOD[order.payment_method] }}</p>
      </section>

      <a v-if="wa" :href="wa" target="_blank" rel="noopener noreferrer" class="btn btn-ghost">💬 Hablar con {{ order.shop_name }}</a>
    </template>
  </div>
</template>

<script>
import api, { errorMessage } from '@/api';
import EmptyState from '@/components/ui/EmptyState.vue';
import StatusBadge from '@/components/ui/StatusBadge.vue';
import { DELIVERY, PAYMENT_METHOD, dateTime, money, whatsappLink } from '@/utils';

export default {
  name: 'OrderView',
  components: { EmptyState, StatusBadge },
  data() {
    return { loading: true, order: null, DELIVERY, PAYMENT_METHOD, paying: false, payError: '', proofError: '', copied: '', timer: null };
  },
  computed: {
    token() { return this.$route.params.token; },
    ins() { return (this.order && this.order.payment_instructions) || {}; },
    timeline() {
      return [{ label: 'Pedido recibido' }, { label: 'Confirmado por la tienda' }, { label: 'Entregado' }];
    },
    progress() {
      return { pending: 0, confirmed: 1, delivered: 2, cancelled: 0 }[this.order.status] || 0;
    },
    wa() {
      return this.order ? whatsappLink(this.order.shop_phone, `Hola! Consulta por mi pedido #${this.order.id} de Multi-Market.`) : null;
    },
    mpReturn() {
      const s = this.$route.query.status || this.$route.query.collection_status;
      if (!s || !this.order || this.order.payment_method !== 'mercadopago') return null;
      if (s === 'approved') return { cls: 'alert-ok', text: 'Mercado Pago informó el pago como aprobado. Estamos confirmándolo con la tienda.' };
      if (s === 'pending' || s === 'in_process') return { cls: 'alert-info', text: 'Tu pago está pendiente de acreditación.' };
      return { cls: 'alert-bad', text: 'El pago no se completó. Podés intentarlo de nuevo.' };
    },
  },
  methods: {
    money, dateTime,
    async load() {
      try {
        this.order = (await api.get(`/api/orders/track/${this.token}/`)).data;
      } catch (e) { this.order = null; } finally { this.loading = false; }
    },
    async payMp() {
      this.paying = true; this.payError = '';
      try {
        const { data } = await api.post(`/api/orders/${this.token}/pay/mercadopago/`);
        window.location.href = data.init_point;
      } catch (e) {
        this.payError = errorMessage(e, 'No pudimos iniciar el pago.'); this.paying = false;
      }
    },
    copy(text) {
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(() => { this.copied = text; setTimeout(() => { this.copied = ''; }, 1500); });
    },
    onProof(ev) {
      const file = ev.target.files[0];
      if (!file) return;
      this.proofError = '';
      const reader = new FileReader();
      reader.onload = async () => {
        try {
          this.order = (await api.post(`/api/orders/track/${this.token}/proof/`, { image_base64: reader.result })).data;
        } catch (e) { this.proofError = errorMessage(e, 'No pudimos subir el comprobante.'); }
      };
      reader.readAsDataURL(file);
    },
  },
  mounted() {
    document.title = 'Mi pedido – Multi-Market';
    this.load();
    // Si se espera una acreditación de Mercado Pago, se actualiza solo.
    this.timer = setInterval(() => {
      if (this.order && this.order.payment_method === 'mercadopago' && ['unpaid', 'pending'].includes(this.order.payment_status) && this.$route.query.status) this.load();
    }, 8000);
  },
  beforeUnmount() { clearInterval(this.timer); },
};
</script>

<style scoped>
.narrow { max-width: 760px; }
.narrow > * + * { margin-top: 14px; }
.head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap; }
.head h1 { margin: 0; }
.timeline { list-style: none; display: flex; justify-content: space-between; margin: 0; position: relative; }
.timeline li { flex: 1; text-align: center; color: var(--muted); font-size: .85rem; font-weight: 600; position: relative; }
.timeline li::before { content: ''; position: absolute; top: 7px; left: -50%; width: 100%; height: 3px; background: #e5e7ef; z-index: 0; }
.timeline li:first-child::before { display: none; }
.dot { display: block; width: 16px; height: 16px; border-radius: 50%; background: #e5e7ef; margin: 0 auto 6px; position: relative; z-index: 1; }
.timeline li.on { color: var(--brand-700); }
.timeline li.on .dot, .timeline li.on::before { background: var(--brand-600); }
.timeline li.bad .dot { background: var(--bad); }
.kv { display: grid; grid-template-columns: 110px 1fr; gap: 6px 12px; margin: 10px 0 14px; }
.kv dt { color: var(--muted); }
.kv dd { margin: 0; font-weight: 600; word-break: break-all; }
.item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border); }
.item.total { border-bottom: 0; font-size: 1.15rem; }
</style>
