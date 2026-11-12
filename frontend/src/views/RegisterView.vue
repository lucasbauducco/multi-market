<template>
  <div class="container page auth">
    <div v-if="done" class="card card-pad ok">
      <div class="big">🎉</div>
      <h1>¡Solicitud enviada!</h1>
      <p>{{ done }}</p>
      <router-link to="/" class="btn">Volver al inicio</router-link>
    </div>

    <form v-else class="card card-pad" @submit.prevent="submit">
      <h1>Vendé en Multi-Market</h1>
      <p class="muted">Creá tu tienda en minutos. Revisamos cada solicitud antes de activarla.</p>
      <div class="field"><label for="rs">Nombre de la tienda / razón social</label><input id="rs" v-model.trim="form.razon_social" class="input" required maxlength="100" /></div>
      <div class="grid-2">
        <div class="field"><label for="cu">CUIT</label><input id="cu" v-model.trim="form.cuit" class="input" required maxlength="11" inputmode="numeric" placeholder="11 dígitos" /></div>
        <div class="field"><label for="ib">Ingresos brutos</label><input id="ib" v-model.trim="form.ingresos_brutos" class="input" required /></div>
      </div>
      <div class="field"><label for="dm">Domicilio</label><input id="dm" v-model.trim="form.domicilio_fiscal" class="input" required maxlength="200" /></div>
      <div class="grid-2">
        <div class="field"><label for="tl">Teléfono / WhatsApp</label><input id="tl" v-model.trim="form.telefono" class="input" placeholder="+54 9 11 5555 0000" /></div>
        <div class="field"><label for="em">Email</label><input id="em" v-model.trim="form.email" type="email" class="input" required /></div>
      </div>
      <div class="grid-2">
        <div class="field"><label for="us">Usuario</label><input id="us" v-model.trim="form.username" class="input" required autocomplete="username" /></div>
        <div class="field"><label for="pw">Contraseña</label><input id="pw" v-model="form.password" type="password" class="input" required minlength="8" autocomplete="new-password" /><span class="hint">Mínimo 8 caracteres.</span></div>
      </div>
      <p v-if="error" class="alert alert-bad">{{ error }}</p>
      <button class="btn btn-lg btn-block" :disabled="busy">{{ busy ? 'Enviando…' : 'Enviar solicitud' }}</button>
      <p class="small muted center">¿Ya tenés cuenta? <router-link to="/ingresar">Ingresar</router-link></p>
    </form>
  </div>
</template>

<script>
import api, { errorMessage } from '@/api';

export default {
  name: 'RegisterView',
  data() {
    return { busy: false, error: '', done: '',
      form: { razon_social: '', cuit: '', domicilio_fiscal: '', ingresos_brutos: '', telefono: '', email: '', username: '', password: '' } };
  },
  methods: {
    async submit() {
      this.busy = true; this.error = '';
      try {
        const payload = { ...this.form };
        if (!payload.telefono) delete payload.telefono;
        this.done = (await api.post('/api/register/', payload)).data.detail;
      } catch (e) { this.error = errorMessage(e, 'No pudimos registrar la tienda.'); } finally { this.busy = false; }
    },
  },
  mounted() { document.title = 'Registrá tu tienda – Multi-Market'; },
};
</script>

<style scoped>
.auth { max-width: 600px; }
.ok { text-align: center; }
.big { font-size: 3rem; }
.center { text-align: center; margin: 14px 0 0; }
</style>
