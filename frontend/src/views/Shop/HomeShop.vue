<template>
  <section class="menu-shop">
    <div class="logo-shop">
      <img :src="computedImage" alt="logo shop" class="circular-image">
      <span class="name-shop">
        {{ userData.razon_social }}
      </span>
    </div>
    <div class="list-menu-shop">
      <router-link to="/shop/products">Inicio</router-link>
      <router-link :to="{ name: 'ShopSearch', query: { shopId: userData.id, isAuthenticate: isAuthenticate, query: userData.razon_social } }">
        Mis Ofertas
      </router-link>



      <router-link to="/shop/sell">Vender</router-link>
    </div>
  </section>
  <router-view :shopId="shopId"></router-view>
  <!-- Si decides usar vistas nombradas para Offers y Categories -->
  <router-view v-if="shopId" name="offers" :shopId="shopId" :isAuthenticate="isAuthenticate" ></router-view>
  <router-view v-if="shopId" name="categories" :shopId="shopId" :isAuthenticate="isAuthenticate"></router-view>
</template>
  
<script>
  import axios from 'axios';
  import router from '@/router';
  export default {
    name: 'HomeShop',
    data() {
      return {
        // Ruta de la imagen guardada en data
        userData: {},
        imagePath: null,
        name: "Mi Ciudad",
        shopId: null,
        isLoading: false,
        allDataLoaded: false,
        isAuthenticate: false,
      };
    },
    computed: {
      computedImage() {
        // Si base64Image es null o está vacía, devuelve la imagen por defecto
        if (!this.imagePath) {
          return require('@/assets/svg/shop.svg');
        }
        // De lo contrario, devuelve la imagen en base64
        return this.imagePath;
      },
    },
    methods: {
      async verifyToken() {
        const token = localStorage.getItem('token');
        const user_id = this.userData.id; // Asegúrate de tener el ID del usuario disponible aquí
        if (!token || !user_id) {
          router.push('/login'); // Si no hay token o user_id, redirige al login
          this.isAuthenticate= false;
          return false;
        }

        console.log(localStorage.getItem('token'))
        console.log(this.userData.id)
        try {
          const config = {
            headers: {
              'Authorization': `Token ${token}`
            }
          };
          await axios.post('http://127.0.0.1:8000/api/token/verify/', { token, user_id }, config); // Asume que este endpoint verifica el token
          this.isAuthenticate= true;
          return true; // El token es válido
        } catch (error) {
          localStorage.removeItem('token'); // Elimina el token ya que no es válido
          localStorage.removeItem('username');
          router.push('/login'); // Redirige al inicio
          this.isAuthenticate= false;
          return false;
        }
      },
      async fetchUserData(username) {
      
      try {
        const token = localStorage.getItem('token');
        console.log(token)
        const config = {
            headers: {
              'Authorization': `Token ${token}`
            }
          };
        const response = await axios.get(`http://127.0.0.1:8000/api/users/${username}/`, config);
        this.userData = response.data[0];
        console.log(response.data)
        this.name = this.userData.razon_social; // O cualquier otro campo relevante
        this.shopId = this.userData.id;
        if (!await this.verifyToken()) return; // Verifica el token antes de proceder
        // Considera marcar al usuario como autenticado aquí si necesitas manejar ese estado
      } catch (error) {
        console.error('Hubo un error al obtener los datos del usuario:', error);
        // Considera manejar errores específicos (p.ej., token expirado) si es necesario
      }
    },
    },
    async mounted() {
      await this.fetchUserData(this.$store.state.username);
    }
    // Otras opciones del componente como data, methods, etc.
  };
  </script>
  
  <style>
  
  </style>