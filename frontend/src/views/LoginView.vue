<template>
  <div class="container page auth">
    <form class="card card-pad" @submit.prevent="login">
      <h1>Ingresar a tu tienda</h1>
      <p class="muted">Accedé al panel para gestionar productos, pedidos y cobros.</p>
      <div class="field"><label for="u">Usuario</label><input id="u" v-model.trim="username" class="input" required autocomplete="username" /></div>
      <div class="field"><label for="p">Contraseña</label><input id="p" v-model="password" type="password" class="input" required autocomplete="current-password" /></div>
      <p v-if="error" class="alert alert-bad">{{ error }}</p>
      <button class="btn btn-lg btn-block" :disabled="busy">{{ busy ? 'Ingresando…' : 'Ingresar' }}</button>
      <p class="small muted center">¿Todavía no vendés con nosotros? <router-link to="/registro">Registrá tu tienda</router-link></p>
    </form>
  </div>
</template>

<script>
import api, { errorMessage } from '@/api';

export default {
  name: 'LoginView',
  data() { return { username: '', password: '', error: '', busy: false }; },
  methods: {
    async login() {
      this.busy = true; this.error = '';
      try {
        const { data } = await api.post('/login/', { username: this.username, password: this.password });
        await this.$store.dispatch('setToken', data.token);
        await this.$store.dispatch('setUserName', data.username);
        await this.$store.dispatch('setRazonSocial', data.razon_social);
        this.$router.push(this.$route.query.next || '/panel');
      } catch (e) {
        this.error = e.response && e.response.status === 401
          ? 'Usuario o contraseña incorrectos, o tu tienda todavía no fue aprobada.'
          : errorMessage(e);
      } finally { this.busy = false; }
    },
  },
  mounted() { document.title = 'Ingresar – Multi-Market'; },
};
</script>

<style scoped>
.auth { max-width: 460px; }
.center { text-align: center; margin: 14px 0 0; }
</style>
