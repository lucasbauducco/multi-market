<template>
    <section class="offers">
        
        <div class="cards-content offers">
        <div class="card" v-for="product in paginatedProducts" :key="product.id">
          <router-link :to="{ name: 'ProductDetails', params: { productId: product.id } }" class="card-link">
            <img :src="product.image_base64" alt="Imagen del producto" class="card-image">
            <div class="card-body">
            <h3 class="card-title">{{ product.name }}</h3>
            <div v-if="product.discount!=0">
                <div class="card-discount">Descuento: - {{ product.discount }}%</div>
                <div class="card-price cross-out">Precio: ${{ product.price }}</div>
                <div class="card-price total">Precio: ${{ product.price - ((product.discount * product.price) / 100 )}}</div>
            </div>
            <div v-else class="card-price total">Precio: ${{ product.price }}</div>
            </div>
          </router-link>
          <div v-if="isAuthenticate" class="btn-card">
              <button @click.stop="editProduct(product.id)">Editar</button>
              <button @click.stop="deleteProduct(product.id)">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                  <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                  <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                </svg>
              </button>
            </div>
        </div>
        <div class="btn-pagination-cards">
            <button type="button" class="carousel__next" @click="nextPageProducts" aria-label="Navigate to next slide">
                <!-- Icono y contenido del botón --><svg class="carousel__icon" viewBox="0 0 24 24" role="img" aria-label="Arrow pointing to the right">
                <title>Arrow pointing to the right</title><path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"></path></svg>
            </button>
            <button type="button" class="carousel__prev" @click="prevPageProducts" aria-label="Navigate to previous slide"><svg class="carousel__icon" viewBox="0 0 24 24" role="img" aria-label="Arrow pointing to the left">
                <title>Arrow pointing to the left</title><path d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z">

                </path>
            </svg>
            </button>
        </div>
        </div>

    </section>
  </template>
  
  <script>
  import axios from 'axios';
  export default {
    name: 'ShopOffers',
    props: ['shopId', 'isAuthenticate'],
    data() {
      return {
        products: [], // Ahora productos se inicializan aquí
        currentPage: 0,
        itemsPerPage: 6, 
      };
    },
    computed: {
        paginatedProducts() {
        const start = this.currentPage * this.itemsPerPage;
        const end = start + this.itemsPerPage;
        return this.products.slice(start, end);
        },
    },
    methods: {
        async loadProducts() {
          try {
              const response = await fetch(`http://127.0.0.1:8000/api/products/shop/${this.shopId}/best_discount/`);
              if (response.ok) {
              const data = await response.json();
              this.products = data; // Asumiendo que la API devuelve un array de productos
              } else {
              console.error("Failed to fetch products");
              }
          } catch (error) {
              console.error("Error fetching products:", error);
          }
      },
      editProduct(productId) {
        this.$router.push({ path: `/product/update/${productId}` });
      },
      async deleteProduct(productId) {
        try {
          const token = localStorage.getItem('token');
          const config = {
            headers: {
              'Authorization': `Token ${token}` // Usa 'Bearer' en lugar de 'Token' si es el esquema esperado por tu backend
            }
          };
            await axios.delete(`http://127.0.0.1:8000/api/products/delete/${productId}/`, config);
            this.products = this.products.filter(product => product.id !== productId);
            alert('Producto eliminado exitosamente');
            // Aquí podrías también actualizar la lista de productos en el cliente, si es necesario
          } catch (error) {
            console.error('Error al eliminar el producto:', error);
            alert('Error al eliminar el producto');
          }
      },
      checkScreenSize() {
        if (window.innerWidth <= 1300) {
          this.itemsPerPage = 2; // Muestra 2 elementos en pantallas pequeñas
        } else {
          this.itemsPerPage = 6; // Muestra 5 elementos en pantallas más grandes
        }
      },
        prevPageProducts() {
        if (this.currentPage > 0) {
          this.currentPage--;
        }
      },
      nextPageProducts() {
        if ((this.currentPage + 1) * this.itemsPerPage < this.products.length) {
          this.currentPage++;
        }
      },
    },
    async mounted() {
        await this.loadProducts();
        await this.checkScreenSize();
        this.interval = setInterval(this.nextPage, 3000); // Cambia página cada 3 segundos
        window.addEventListener('resize', this.checkScreenSize);
    },
    beforeUnmount() {
        clearInterval(this.interval); // Limpia el intervalo
        window.removeEventListener('resize', this.checkScreenSize);
    },
  }
  </script>
  
  <style>
  /* Estilos relevantes a Offers aquí */
  .card-link {
  text-decoration: none; /* Elimina el subrayado de los enlaces */
  color: inherit; /* Hace que el color del texto sea el mismo que el de su elemento padre */
  /* Agrega aquí cualquier otro estilo que desees */
}
  </style>