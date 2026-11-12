<template>
  <div class="container page">
    <!-- Confirmación -->
    <section v-if="placed.length" class="done">
      <div class="card card-pad ok-head">
        <div class="big">🎉</div>
        <h1>¡Gracias por tu compra, {{ form.buyer_name.split(' ')[0] }}!</h1>
        <p class="muted">Creamos {{ placed.length }} pedido{{ placed.length > 1 ? 's' : '' }}. Guardá los enlaces: te permiten seguirlos sin crear cuenta.</p>
      </div>
      <article v-for="o in placed" :key="o.id" class="card card-pad order">
        <div class="row">
          <strong>Pedido #{{ o.id }} · {{ o.shop_name }}</strong>
          <span class="spacer"></span>
          <strong>{{ money(o.total) }}</strong>
        </div>
        <div class="muted small">{{ methodLabel(o.payment_method) }} · {{ DELIVERY[o.delivery_method] }}</div>
        <p v-if="payError[o.id]" class="error-text">{{ payError[o.id] }}</p>
        <div class="row">
          <button v-if="o.payment_method === 'mercadopago'" class="btn btn-accent" :disabled="paying === o.id" @click="payMp(o)">
            {{ paying === o.id ? 'Redirigiendo…' : 'Pagar con Mercado Pago' }}
          </button>
          <router-link :to="`/pedido/${o.public_token}`" class="btn" :class="o.payment_method === 'mercadopago' ? 'btn-ghost' : ''">
            {{ o.payment_method === 'mercadopago' ? 'Ver pedido' : 'Ver instrucciones de pago' }}
          </router-link>
        </div>
      </article>
      <router-link to="/" class="btn btn-ghost">Seguir comprando</router-link>
    </section>

    <!-- Checkout -->
    <template v-else>
      <h1>Finalizar compra</h1>
      <empty-state v-if="!groups.length" icon="🛒" title="Tu carrito está vacío" to="/buscar" cta="Explorar productos" />

      <div v-else class="layout">
        <section class="stack">
          <ol class="steps" aria-label="Pasos">
            <li v-for="(s, i) in steps" :key="s" :class="{ on: step === i, done: step > i }" @click="step > i && (step = i)">
              <span class="n">{{ step > i ? '✓' : i + 1 }}</span>{{ s }}
            </li>
          </ol>

          <!-- 1. Datos -->
          <form v-show="step === 0" class="card card-pad" @submit.prevent="next">
            <h2>Tus datos</h2>
            <div class="grid-2">
              <div class="field"><label for="n">Nombre y apellido</label><input id="n" v-model.trim="form.buyer_name" class="input" required maxlength="120" autocomplete="name" /></div>
              <div class="field"><label for="t">Teléfono / WhatsApp</label><input id="t" v-model.trim="form.buyer_phone" class="input" required maxlength="40" autocomplete="tel" placeholder="+54 9 11 5555 0000" /></div>
            </div>
            <div class="field"><label for="e">Email <span class="muted">(opcional, para el comprobante)</span></label><input id="e" v-model.trim="form.buyer_email" type="email" class="input" autocomplete="email" /></div>
            <button class="btn btn-lg" type="submit">Continuar</button>
          </form>

          <!-- 2. Entrega -->
          <form v-show="step === 1" class="card card-pad" @submit.prevent="next">
            <h2>Entrega</h2>
            <label class="opt" :class="{ on: form.delivery_method === 'pickup' }">
              <input v-model="form.delivery_method" type="radio" value="pickup" />
              <div><strong>Retiro en el local</strong><div class="muted small">Coordinás día y horario con la tienda. Sin costo.</div></div>
            </label>
            <label class="opt" :class="{ on: form.delivery_method === 'shipping' }">
              <input v-model="form.delivery_method" type="radio" value="shipping" />
              <div><strong>Envío a domicilio</strong><div class="muted small">La tienda te confirma costo y plazo por WhatsApp.</div></div>
            </label>
            <div v-if="form.delivery_method === 'shipping'" class="field">
              <label for="a">Dirección de entrega</label>
              <input id="a" v-model.trim="form.shipping_address" class="input" maxlength="250" placeholder="Calle, número, localidad" :required="form.delivery_method === 'shipping'" autocomplete="street-address" />
            </div>
            <div class="field"><label for="no">Notas para la tienda <span class="muted">(opcional)</span></label><textarea id="no" v-model.trim="form.notes" class="input" maxlength="500"></textarea></div>
            <div class="row"><button type="button" class="btn btn-ghost" @click="step = 0">Atrás</button><button class="btn btn-lg" type="submit">Continuar</button></div>
          </form>

          <!-- 3. Pago -->
          <section v-show="step === 2" class="card card-pad">
            <h2>Medio de pago</h2>
            <p v-if="loadingMethods" class="muted">Cargando medios de pago…</p>
            <div v-for="g in groups" :key="g.shop" class="paygroup">
              <div class="row"><strong>🏪 {{ g.shop_name }}</strong><span class="spacer"></span><span class="muted">{{ money(g.total) }}</span></div>
              <p v-if="!methodsFor(g.shop).length && !loadingMethods" class="alert alert-bad small">Esta tienda no tiene medios de pago disponibles. Quitá sus productos del carrito.</p>
              <label v-for="m in methodsFor(g.shop)" :key="m.code" class="opt" :class="{ on: payment[g.shop] === m.code }">
                <input v-model="payment[g.shop]" type="radio" :name="`pay-${g.shop}`" :value="m.code" />
                <div>
                  <strong>{{ m.label }}</strong> <span v-if="m.online" class="badge badge-ok">Online</span>
                  <div class="muted small">{{ m.description }}</div>
                </div>
              </label>
            </div>
            <div class="row"><button type="button" class="btn btn-ghost" @click="step = 1">Atrás</button><button class="btn btn-lg" :disabled="!paymentsReady" @click="next">Continuar</button></div>
          </section>

          <!-- 4. Confirmar -->
          <section v-show="step === 3" class="card card-pad">
            <h2>Revisá y confirmá</h2>
            <dl class="review">
              <dt>Contacto</dt><dd>{{ form.buyer_name }} · {{ form.buyer_phone }}<span v-if="form.buyer_email"> · {{ form.buyer_email }}</span></dd>
              <dt>Entrega</dt><dd>{{ DELIVERY[form.delivery_method] }}<span v-if="form.delivery_method === 'shipping'"> · {{ form.shipping_address }}</span></dd>
              <dt v-for="g in groups" :key="`d${g.shop}`">{{ g.shop_name }}</dt>
              <dd v-for="g in groups" :key="`dd${g.shop}`">{{ methodLabel(payment[g.shop]) }} · {{ money(g.total) }}</dd>
            </dl>
            <p v-if="error" class="alert alert-bad">{{ error }}</p>
            <p class="small muted">Al confirmar aceptás los <router-link to="/terminos">términos y condiciones</router-link>.</p>
            <div class="row"><button type="button" class="btn btn-ghost" @click="step = 2">Atrás</button>
              <button class="btn btn-accent btn-lg" :disabled="sending" @click="submit">{{ sending ? 'Enviando…' : `Confirmar pedido · ${money(cartTotal)}` }}</button></div>
          </section>
        </section>

        <!-- Resumen fijo -->
        <aside class="summary card card-pad">
          <h2>Tu pedido</h2>
          <div v-for="i in cart" :key="i.id" class="mini">
            <img v-if="i.image" :src="i.image" alt="" /><div v-else class="ph"></div>
            <div class="grow"><div class="mname">{{ i.name }}</div><span class="muted small">x{{ i.quantity }}</span></div>
            <span>{{ money(i.price * i.quantity) }}</span>
          </div>
          <div class="srow total"><span>Total</span><strong>{{ money(cartTotal) }}</strong></div>
          <router-link to="/carrito" class="small">Editar carrito</router-link>
        </aside>
      </div>
    </template>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import api, { errorMessage } from '@/api';
import EmptyState from '@/components/ui/EmptyState.vue';
import { DELIVERY, PAYMENT_METHOD, money } from '@/utils';

export default {
  name: 'CheckoutView',
  components: { EmptyState },
  data() {
    return {
      step: 0, steps: ['Datos', 'Entrega', 'Pago', 'Confirmar'], DELIVERY,
      form: { buyer_name: '', buyer_phone: '', buyer_email: '', delivery_method: 'pickup', shipping_address: '', notes: '' },
      methods: {}, payment: {}, loadingMethods: true,
      sending: false, error: '', placed: [], paying: null, payError: {},
    };
  },
  computed: {
    ...mapState(['cart']),
    ...mapGetters(['cartTotal', 'cartByShop']),
    groups() { return this.cartByShop; },
    paymentsReady() { return this.groups.length > 0 && this.groups.every(g => this.payment[g.shop]); },
  },
  methods: {
    money,
    methodLabel(code) { return PAYMENT_METHOD[code] || code || ''; },
    methodsFor(shop) { return (this.methods[shop] && this.methods[shop].methods) || []; },
    next() { this.step += 1; window.scrollTo({ top: 0, behavior: 'smooth' }); },
    async loadMethods() {
      if (!this.groups.length) { this.loadingMethods = false; return; }
      try {
        const { data } = await api.get('/api/checkout/methods/', { params: { shops: this.groups.map(g => g.shop).join(',') } });
        this.methods = data;
        this.groups.forEach((g) => {
          const list = this.methodsFor(g.shop);
          if (list.length) this.payment[g.shop] = list[0].code;
        });
      } catch (e) { /* se informa en el paso de pago */ } finally { this.loadingMethods = false; }
    },
    async submit() {
      this.sending = true;
      this.error = '';
      try {
        const payload = {
          ...this.form,
          items: this.cart.map(i => ({ product: i.id, quantity: i.quantity })),
          payment_methods: Object.fromEntries(this.groups.map(g => [String(g.shop), this.payment[g.shop]])),
        };
        if (!payload.buyer_email) delete payload.buyer_email;
        const { data } = await api.post('/api/checkout/', payload);
        this.placed = data;
        this.$store.dispatch('clearCart');
        window.scrollTo({ top: 0 });
      } catch (e) {
        this.error = errorMessage(e, 'No pudimos crear el pedido.');
      } finally {
        this.sending = false;
      }
    },
    async payMp(order) {
      this.paying = order.id;
      this.payError = { ...this.payError, [order.id]: '' };
      try {
        const { data } = await api.post(`/api/orders/${order.public_token}/pay/mercadopago/`);
        window.location.href = data.init_point;
      } catch (e) {
        this.payError = { ...this.payError, [order.id]: errorMessage(e, 'No pudimos iniciar el pago.') };
        this.paying = null;
      }
    },
  },
  mounted() {
    document.title = 'Finalizar compra – Multi-Market';
    this.loadMethods();
  },
};
</script>

<style scoped>
.layout { display: grid; grid-template-columns: 1fr 340px; gap: 20px; align-items: start; margin-top: 12px; }
.steps { list-style: none; display: flex; gap: 6px; padding: 0; margin: 0; flex-wrap: wrap; }
.steps li { flex: 1; min-width: 110px; display: flex; align-items: center; gap: 8px; padding: 10px 12px; background: #fff; border: 1px solid var(--border); border-radius: 10px; color: var(--muted); font-weight: 600; }
.steps li.on { border-color: var(--brand-600); color: var(--brand-700); background: var(--brand-50); }
.steps li.done { color: var(--ok); cursor: pointer; }
.n { width: 24px; height: 24px; border-radius: 50%; display: grid; place-items: center; background: #e5e7ef; font-size: .8rem; }
.on .n { background: var(--brand-600); color: #fff; }
.done .n { background: var(--ok-bg); color: var(--ok); }
.opt { display: flex; gap: 12px; align-items: flex-start; padding: 14px; border: 1px solid var(--border); border-radius: 12px; margin-bottom: 10px; cursor: pointer; }
.opt.on { border-color: var(--brand-600); background: var(--brand-50); }
.opt input { margin-top: 4px; }
.paygroup { border-top: 1px solid var(--border); padding-top: 12px; margin-top: 12px; }
.review { display: grid; grid-template-columns: 150px 1fr; gap: 8px 16px; margin: 0 0 14px; }
.review dt { color: var(--muted); }
.review dd { margin: 0; }
.summary { position: sticky; top: 130px; display: flex; flex-direction: column; gap: 10px; }
.summary h2 { margin: 0; }
.mini { display: flex; align-items: center; gap: 10px; }
.mini img, .ph { width: 46px; height: 46px; border-radius: 8px; object-fit: cover; background: #eef0f7; }
.grow { flex: 1; min-width: 0; }
.mname { font-weight: 600; font-size: .9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.srow { display: flex; justify-content: space-between; }
.total { font-size: 1.2rem; border-top: 1px solid var(--border); padding-top: 10px; }
.done { max-width: 720px; margin: 0 auto; display: flex; flex-direction: column; gap: 14px; align-items: stretch; }
.ok-head { text-align: center; }
.big { font-size: 3rem; }
.order { display: flex; flex-direction: column; gap: 8px; }
@media (max-width: 900px) { .layout { grid-template-columns: 1fr; } .summary { position: static; } .review { grid-template-columns: 1fr; } }
</style>
