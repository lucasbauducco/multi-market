<template>
    <div>
      <h2>Login</h2>
      <form @submit.prevent="login">
        <input type="text" v-model="username" placeholder="Username" />
        <input type="password" v-model="password" placeholder="Password" />
        <p v-if="error" style="color:#b00020">{{ error }}</p>
        <button type="submit">Ingresar</button>
        <router-link to="/register">Registrar mi tienda</router-link>
      </form>
    </div>
  </template>
  
  <script>
  import api, { errorMessage } from '@/api';
  import { mapActions } from 'vuex';
  
  export default {
    data() {
      return {
        username: '',
        password: '',
        error: ''
      };
    },
    methods: {
      ...mapActions(['setToken','setUserName']),
      async login() {
        this.error = '';
        try {
          const response = await api.post('/login/', {
            username: this.username,
            password: this.password
          });
          this.setToken(response.data.token);
          this.setUserName(this.username);
          this.$router.push({ name: 'shop' });
        } catch (error) {
          this.error = error.response && error.response.status === 401
            ? 'Usuario o contraseña incorrectos, o la tienda aún no fue aprobada.'
            : errorMessage(error);
        }
      }
    }
  };
  </script>