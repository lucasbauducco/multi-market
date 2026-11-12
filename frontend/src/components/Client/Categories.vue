<template>
  <section class="categories">
      <span class="title-secondary">
        Categories
      </span>
      <div class="category" v-for="(category, index) in categories" :key="index" :ref="`category-${category.id}`" :data-category-id="category.id">
        <div v-if="category.productsLoaded">
          <h2 class="title-text">{{ category.name }}</h2>
          <div class="cards-content">
            <div class="card" v-for="product in paginatedProductsCategory(category.id)" :key="product.id">
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
                  <!-- Otros detalles del producto -->
                  <div v-if="isAuthenticate" class="btn-card">
                    <button @click.stop="editProduct(product.id)">Editar</button>
                    <button @click="deleteProduct(product.id)">
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                        <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                        <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </router-link>
            </div>
            <div class="btn-pagination-cards">
                <button type="button" class="carousel__next" @click="nextPageCategory(category)" aria-label="Navigate to next slide"><svg class="carousel__icon" viewBox="0 0 24 24" role="img" aria-label="Arrow pointing to the right">
                  <title>Arrow pointing to the right</title><path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"></path></svg>
                </button>
                <button type="button" class="carousel__prev" @click="prevPageCategory(category)" aria-label="Navigate to previous slide"><svg class="carousel__icon" viewBox="0 0 24 24" role="img" aria-label="Arrow pointing to the left">
                  <title>Arrow pointing to the left</title><path d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z">

                  </path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  </template>
  
  <script>
  import axios from 'axios';
  export default {
    name: 'ShopCategories',
    props: ['shopId', 'isAuthenticate'],
    data() {
      return {
        categories: [],
        products: [],
        currentPage: 0,
        currentCategory: 0,
        itemsPerPage: 5,
        categoriesPerPage: 1,
        isLoading: false,
        observer: null,
        allDataLoaded: false,
      };
    },
    computed: {
      paginatedProducts() {
        const start = this.currentPage * this.itemsPerPage;
        const end = start + this.itemsPerPage;
        return this.products.slice(start, end);
      },
      paginatedProductsCategory() {
        // Esta función computada devuelve otra función
        return (categoryId) => {
          // Encuentra la categoría basada en categoryId
          const category = this.categories.find(cat => cat.id === categoryId);
          if (!category || !category.products) return [];
          
          // Calcula el rango de productos a mostrar
          const start = category.currentPage * this.itemsPerPage;
          const end = start + this.itemsPerPage;
          
          // Devuelve los productos de esa categoría que caen dentro del rango
          return category.products.slice(start, end);
        };
      },
    },
    methods: {
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
            this.categories.forEach(category => {
              category.products = category.products.filter(product => product.id !== productId);
            });
            alert('Producto eliminado exitosamente');
            // Aquí podrías también actualizar la lista de productos en el cliente, si es necesario
          } catch (error) {
            console.error('Error al eliminar el producto:', error);
            alert('Error al eliminar el producto');
          }
      },
      async loadCategoryProducts(categoryId) {
        const categoryIdNumber = parseInt(categoryId, 10);
        const categoryIndex = this.categories.findIndex(cat => cat.id === categoryIdNumber);
        if (categoryIndex === -1) {
          console.error("Categoría no encontrada:", categoryId);
          return;
        }
        if (this.categories[categoryIndex].productsLoaded) {
          return;
        }
        try {
          const response = await axios.get(`http://127.0.0.1:8000/api/products/shop/${this.shopId}/category/${categoryId}`);
            // Asigna el array de resultados a la categoría
            if(response.data.results && response.data.results.length > 0){
                this.categories[categoryIndex].productsLoaded = true;
                this.categories[categoryIndex].products = response.data.results;
            }
        } catch (error) {
          console.error("Error loading category products:", error);
        }
      },
      observeCategories() {
        const options = {
          root: null,
          rootMargin: '0px',
          threshold: 0.1
        };
        this.observer = new IntersectionObserver((entries, observer) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              const categoryId = entry.target.dataset.categoryId; // Asegúrate de que cada elemento de categoría tenga un data-category-id
              this.loadCategoryProducts(categoryId);
              observer.unobserve(entry.target);
            }
          });
        }, options);

        this.categories.forEach(category => {
          const categoryElement = this.$refs[`category-${category.id}`][0]; // Accede al elemento DOM usando el ref dinámico
          if (categoryElement) {
            this.observer.observe(categoryElement);
          }
        });
      },
      async loadCategories() {
          try {
              const response = await axios.get(`http://127.0.0.1:8000/api/categories/shop/${this.shopId}`);
              // Asegúrate de inicializar currentPage para cada categoría
              this.categories = response.data.map(category => ({ ...category, productsLoaded: false, currentPage: 0 }));
              this.$nextTick(() => {
                  this.observeCategories();
              });
          } catch (error) {
              console.error("Error loading categories:", error);
          }
      },
      handleScroll() {
        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
        
        if (clientHeight + scrollTop >= scrollHeight - 5 && !this.isLoading) { // Se ajusta el '-5' para controlar cuán cerca del final se activa la carga
          this.loadMoreCategories();
        }
      },
      checkScreenSize() {
        if (window.innerWidth <= 1300) {
          this.itemsPerPage = 2; // Muestra 2 elementos en pantallas pequeñas
        } else {
          this.itemsPerPage = 5; // Muestra 5 elementos en pantallas más grandes
        }
      },
      prevPageCategory(category) {
        if (category.currentPage > 0) {
          category.currentPage--;
        }
      },
      nextPageCategory(category) {
        if ((category.currentPage + 1) * this.itemsPerPage < category.products.length) {
          category.currentPage++;
        }
      },
    },
    async mounted() {
        await this.loadCategories();
        await this.checkScreenSize();
        this.interval = setInterval(this.nextPage, 3000); // Cambia página cada 3 segundos
        window.addEventListener('resize', this.checkScreenSize);
        //window.addEventListener('scroll', this.handleScroll);
    },
    beforeUnmount() {
        clearInterval(this.interval); // Limpia el intervalo
        window.removeEventListener('resize', this.checkScreenSize);
        //window.removeEventListener('scroll', this.handleScroll);
    },
  }
  </script>
  
  <style>
  /* Estilos relevantes a Categories aquí */
  </style>