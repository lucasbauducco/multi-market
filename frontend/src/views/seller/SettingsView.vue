<template>
  <div class="stack">
    <h1>Configuración y cobros</h1>
    <p v-if="flash" class="alert" :class="flash.cls">{{ flash.text }}</p>

    <!-- Perfil -->
    <form class="card card-pad" @submit.prevent="saveProfile">
      <h2>Perfil público de la tienda</h2>
      <p class="muted small">Así se ve tu página <router-link v-if="profile.slug" :to="`/tienda/${profile.slug}`">/tienda/{{ profile.slug }}</router-link>.</p>
      <div class="field"><label for="d">Descripción</label><textarea id="d" v-model.trim="profile.description" class="input" maxlength="1000" placeholder="Contá qué vendés, tu horario y zona de entrega"></textarea></div>
      <div class="grid-2">
        <div class="field"><label class="label">Logo</label>
          <div class="up"><img v-if="logoPreview || profile.logo" :src="logoPreview || profile.logo" alt="Logo" class="lg" /><input type="file" accept="image/*" @change="pick($event, 'logo')" /></div></div>
        <div class="field"><label class="label">Banner</label>
          <div class="up"><img v-if="bannerPreview || profile.banner" :src="bannerPreview || profile.banner" alt="Banner" class="bn" /><input type="file" accept="image/*" @change="pick($event, 'banner')" /></div></div>
      </div>
      <button class="btn" :disabled="busyProfile">{{ busyProfile ? 'Guardando…' : 'Guardar perfil' }}</button>
    </form>

    <!-- Mercado Pago -->
    <section class="card card-pad">
      <div class="row"><h2>Mercado Pago</h2><span class="spacer"></span><span class="badge" :class="pay.mp_connected ? 'badge-ok' : 'badge-neutral'">{{ pay.mp_connected ? 'Conectado' : 'No conectado' }}</span></div>
      <p class="muted">Cobrá con tarjetas, dinero en cuenta y QR. El dinero va directo a tu cuenta de Mercado Pago.</p>
      <p v-if="!pay.mp_platform_configured" class="alert alert-warn small">La plataforma todavía no tiene las credenciales de Mercado Pago configuradas (variables <code>MP_CLIENT_ID</code> y <code>MP_CLIENT_SECRET</code> en el servidor). Cuando estén, vas a poder conectar tu cuenta desde acá.</p>
      <div class="row">
        <button v-if="!pay.mp_connected" class="btn btn-accent" :disabled="!pay.mp_platform_configured || connecting" @click="connectMp">{{ connecting ? 'Redirigiendo…' : 'Conectar Mercado Pago' }}</button>
        <template v-else>
          <label class="checkbox"><input v-model="pay.mp_enabled" type="checkbox" @change="savePay" /> Ofrecer Mercado Pago en mi tienda</label>
          <button class="btn btn-ghost btn-sm" @click="disconnectMp">Desconectar</button>
        </template>
      </div>
    </section>

    <!-- Otros medios -->
    <form class="card card-pad" @submit.prevent="savePay">
      <h2>Otros medios de pago</h2>

      <label class="checkbox sw"><input v-model="pay.accepts_cash" type="checkbox" /> <strong>Efectivo / retiro en local / contra entrega</strong></label>
      <div v-if="pay.accepts_cash" class="field ind"><label for="ci">Instrucciones para el comprador</label><input id="ci" v-model.trim="pay.cash_instructions" class="input" maxlength="300" placeholder="Ej: Retiro de lunes a viernes 9 a 18 hs en Av. Siempreviva 123" /></div>

      <label class="checkbox sw"><input v-model="pay.accepts_transfer" type="checkbox" /> <strong>Transferencia bancaria</strong></label>
      <div v-if="pay.accepts_transfer" class="ind">
        <div class="grid-2">
          <div class="field"><label for="th">Titular</label><input id="th" v-model.trim="pay.transfer_holder" class="input" maxlength="120" /></div>
          <div class="field"><label for="ta">Alias</label><input id="ta" v-model.trim="pay.transfer_alias" class="input" maxlength="40" /></div>
        </div>
        <div class="field"><label for="tc">CBU / CVU</label><input id="tc" v-model.trim="pay.transfer_cbu" class="input" maxlength="22" inputmode="numeric" placeholder="22 dígitos" /></div>
      </div>

      <label class="checkbox sw"><input v-model="pay.accepts_link" type="checkbox" /> <strong>Link de pago propio</strong> <span class="muted small">(Ualá Bis, MODO, PayPal.me, etc.)</span></label>
      <div v-if="pay.accepts_link" class="ind grid-2">
        <div class="field"><label for="ll">Nombre a mostrar</label><input id="ll" v-model.trim="pay.link_label" class="input" maxlength="40" placeholder="Ualá Bis" /></div>
        <div class="field"><label for="lu">Link (https://)</label><input id="lu" v-model.trim="pay.link_url" type="url" class="input" placeholder="https://..." /></div>
      </div>

      <p v-if="payError" class="alert alert-bad">{{ payError }}</p>
      <button class="btn" :disabled="busyPay">{{ busyPay ? 'Guardando…' : 'Guardar medios de pago' }}</button>
    </form>
  </div>
</template>

<script>
import api, { errorMessage } from '@/api';

export default {
  name: 'SettingsView',
  data() {
    return { profile: { description: '', slug: '', logo: null, banner: null }, pay: {}, logoData: null, bannerData: null, logoPreview: '', bannerPreview: '',
      busyProfile: false, busyPay: false, payError: '', connecting: false, flash: null };
  },
  methods: {
    pick(e, which) {
      const file = e.target.files[0];
      if (!file) return;
      const r = new FileReader();
      r.onload = () => { this[`${which}Data`] = r.result; this[`${which}Preview`] = r.result; };
      r.readAsDataURL(file);
    },
    async saveProfile() {
      this.busyProfile = true;
      try {
        const body = { description: this.profile.description };
        if (this.logoData) body.logo_base64 = this.logoData;
        if (this.bannerData) body.banner_base64 = this.bannerData;
        this.profile = (await api.patch('/api/shop/profile/', body)).data;
        this.logoData = this.bannerData = null; this.logoPreview = this.bannerPreview = '';
        this.flash = { cls: 'alert-ok', text: 'Perfil actualizado.' };
      } catch (e) { this.flash = { cls: 'alert-bad', text: errorMessage(e) }; } finally { this.busyProfile = false; }
    },
    async savePay() {
      this.busyPay = true; this.payError = '';
      try {
        const keys = ['accepts_cash', 'cash_instructions', 'accepts_transfer', 'transfer_holder', 'transfer_alias', 'transfer_cbu', 'accepts_link', 'link_label', 'link_url', 'mp_enabled'];
        const body = Object.fromEntries(keys.map(k => [k, this.pay[k]]));
        this.pay = (await api.patch('/api/shop/payment-settings/', body)).data;
        this.flash = { cls: 'alert-ok', text: 'Medios de pago actualizados.' };
      } catch (e) { this.payError = errorMessage(e); } finally { this.busyPay = false; }
    },
    async connectMp() {
      this.connecting = true;
      try { window.location.href = (await api.get('/api/payments/mercadopago/connect/')).data.url; } catch (e) { this.flash = { cls: 'alert-bad', text: errorMessage(e) }; this.connecting = false; }
    },
    async disconnectMp() {
      if (!confirm('¿Desconectar Mercado Pago? Dejarás de cobrar con ese medio.')) return;
      this.pay = (await api.post('/api/payments/mercadopago/disconnect/')).data;
    },
  },
  async mounted() {
    document.title = 'Configuración – Multi-Market';
    const mp = this.$route.query.mp;
    if (mp === 'connected') this.flash = { cls: 'alert-ok', text: '¡Mercado Pago conectado correctamente!' };
    if (mp === 'error') this.flash = { cls: 'alert-bad', text: 'No pudimos conectar Mercado Pago. Intentá de nuevo.' };
    try {
      const [p, s] = await Promise.all([api.get('/api/shop/profile/'), api.get('/api/shop/payment-settings/')]);
      this.profile = p.data; this.pay = s.data;
    } catch (e) { this.flash = { cls: 'alert-bad', text: errorMessage(e) }; }
  },
};
</script>

<style scoped>
.sw { margin: 16px 0 8px; }
.ind { margin-left: 26px; }
.up { display: flex; flex-direction: column; gap: 8px; }
.lg { width: 84px; height: 84px; border-radius: 16px; object-fit: cover; }
.bn { width: 100%; max-height: 90px; border-radius: 10px; object-fit: cover; }
code { background: #eef0f7; padding: 1px 5px; border-radius: 4px; }
</style>
