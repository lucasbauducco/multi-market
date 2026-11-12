<template>
    <div>
      <h2>Login</h2>
      <form @submit.prevent="login">
        <input type="text" v-model="username" placeholder="Username" />
        <input type="password" v-model="password" placeholder="Password" />
        <button type="submit">Login</button>
      </form>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { mapActions } from 'vuex';
  
  export default {
    data() {
      return {
        username: '',
        password: ''
      };
    },
    methods: {
      ...mapActions(['setToken','setUserName']),
      async login() {
        try {
          const response = await axios.post('http://localhost:8000/login/', {
            username: this.username,
            password: this.password
          });
          this.setToken(response.data.token);
          this.setUserName(this.username);
          this.$router.push({ name: 'shop' });
        } catch (error) {
          console.error('Error en el login:', error);
        }
      }
    }
  };
  </script>