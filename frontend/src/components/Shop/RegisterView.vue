<template>
  <section class="register">
    <h2>Registrá tu tienda</h2>
    <p v-if="done" class="ok">{{ done }}</p>
    <form v-else @submit.prevent="submit">
      <input v-model.trim="form.razon_social" placeholder="Nombre / razón social" required />
      <input v-model.trim="form.cuit" placeholder="CUIT (11 dígitos)" required maxlength="11" inputmode="numeric" />
      <input v-model.trim="form.domicilio_fiscal" placeholder="Domicilio" required />
      <input v-model.trim="form.ingresos_brutos" placeholder="Ingresos brutos" required />
      <input v-model.trim="form.telefono" placeholder="Teléfono (ej. +5491155550000)" />
      <input v-model.trim="form.email" type="email" placeholder="Email" required />
      <input v-model.trim="form.username" placeholder="Usuario" required autocomplete="username" />
      <input v-model="form.password" type="password" placeholder="Contraseña (mín. 8)" required minlength="8"
             autocomplete="new-password" />
      <p v-if="error" class="error">{{ error }}</p>
      <button type="submit" :disabled="sending">{{ sending ? 'Enviando…' : 'Enviar solicitud' }}</button>
      <small>Revisamos cada solicitud antes de activar la tienda.</small>
    </form>
    <router-link to="/login">Ya tengo cuenta</router-link>
  </section>
</template>

<script>
import api, { errorMessage } from '@/api';

export default {
  name: 'RegisterView',
  data() {
    return {
      form: { razon_social: '', cuit: '', domicilio_fiscal: '', ingresos_brutos: '', telefono: '',
              email: '', username: '', password: '' },
      sending: false,
      error: '',
      done: '',
    };
  },
  methods: {
    async submit() {
      this.sending = true;
      this.error = '';
      try {
        const payload = { ...this.form };
        if (!payload.telefono) delete payload.telefono;
        const { data } = await api.post('/api/register/', payload);
        this.done = data.detail;
      } catch (e) {
        this.error = errorMessage(e, 'No pudimos registrar la tienda.');
      } finally {
        this.sending = false;
      }
    },
  },
};
</script>

<style scoped>
.register { max-width: 420px; margin: 2rem auto; padding: 0 1rem; }
form { display: flex; flex-direction: column; gap: .6rem; margin-bottom: 1rem; }
input { padding: .5rem; }
.error { color: #b00020; }
.ok { background: #e8f5e9; padding: 1rem; border-radius: 8px; }
</style>
