<template>
  <section class="createProduct">
    <section class="form">
      <h2>Update Product</h2>
      <form @submit.prevent="updateProduct">
        <div>
          <label for="name">Name:</label>
          <input type="text" id="name" v-model="product.name">
        </div>
        <div>
          <label for="description">Description:</label>
          <textarea id="description" v-model="product.description"></textarea>
        </div>
        <div>
          <label for="price">Price:</label>
          <input type="number" id="price" v-model="product.price">
        </div>
        <div>
          <label for="barcode">Barcode:</label>
          <input type="text" id="barcode" v-model="product.barcode" disabled>
        </div>
        <div>
          <label for="discount">Discount:</label>
          <input type="number" id="discount" v-model="product.discount">
        </div>
        <div>
          <label for="subcategory">Subcategoría:</label>
                    <label for="subcategorySearch">Buscar Subcategoría:</label>
                    <input type="text" v-model="searchQuery" @input="filterOptions" placeholder="Buscar subcategoría...">
                    <select id="subcategory" v-model="product.subcategory">
                        <option value="" disabled>Seleccione una subcategoría</option>
                        <option v-for="subcat in filteredSubcategories" :key="subcat.id" :value="subcat.id">
                            {{ subcat.name }}
                        </option>
                    </select>
        </div>
        <!-- Additional fields as necessary -->
        <button type="submit">Update Product</button>
      </form>
    </section>
    <div class="card" :key="product.id">
        <img :src="product.image_base64" alt="Imagen del producto" class="card-image">
        <div class="card-body">
        <h3 class="card-title">{{ product.name }}</h3>
        <p class="card-description">{{ product.description }}</p>
        <div class="card-discount">Descuento: - {{ product.discount }}%</div>
        <div class="card-price total">Precio: ${{ product.price }}</div>
        <!-- Otros detalles del producto -->
        </div>
    </div>
  </section>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        product: {
          id: this.$route.params.id,
          name: '',
          description: '',
          price: 0,
          barcode: '',
          discount: 0,
          subcategory: null,
        },
        subcategories: [], // Assume you fetch this from another endpoint
        searchQuery: '',
        filteredSubcategories: [],
      };
    },
    async created() {
      await this.fetchSubcategories(); 
      await this.fetchProductDetails();
      this.filterOptions();
    },
    methods: {
      async fetchProductDetails() {
        try {
        // Obtiene el token desde el estado global (Vuex Store)
        const token = this.$store.state.token;
        const productId = this.product.id;
        // Configura las cabeceras de la solicitud
        const config = {
          headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}` // Usa 'Bearer' en lugar de 'Token' si es el esquema esperado por tu backend
          }
        };
          const response = await axios.get(`http://127.0.0.1:8000/api/product/${productId}/`, config);
          this.product = { ...this.product, ...response.data };
          this.filterOptions();
        } catch (error) {
          console.error("Error fetching product details:", error);
          // Manejo de errores (p.ej., mostrar un mensaje al usuario)
        }
      },
      updateProduct() {
        const token = this.$store.state.token;
        const productId = this.product.id;
        // Configura las cabeceras de la solicitud
        const config = {
          headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}` // Usa 'Bearer' en lugar de 'Token' si es el esquema esperado por tu backend
          }
        };
        axios.put(`http://127.0.0.1:8000/api/product/${productId}/`, this.product, config)
          .then(response => {
            alert('Product updated successfully', response);
            // Redirect or perform some action upon success
          })
          .catch(error => {
            console.error("There was an error updating the product: ", error);
          });
      },
      filterOptions() {
         // Asume que quieres todas las subcategorías filtradas inicialmente
          if (this.searchQuery) {
            this.filteredSubcategories = this.subcategories.filter((subcat) =>
              subcat.name.toLowerCase().includes(this.searchQuery.toLowerCase())
            );
          }
        },
        fetchSubcategories() {
            axios.get('http://127.0.0.1:8000/api/subcategories/')
                .then(response => {
                  this.subcategories = response.data;
                  this.setInitialSubcategory();
                })
                .catch(error => {
                console.error('Hubo un error al cargar las subcategorías:', error);
                });
        },
        setInitialSubcategory() {
            if (this.product.subcategory) {
                this.searchQuery = this.subcategories.find(subcat => subcat.id === this.product.subcategory)?.name || '';
                this.filterOptions(); // Asegúrate de que la lista filtrada se actualice si es necesario
            }
        }
    }
  };
  </script>
  
  <style scoped>
  /* Add your CSS styling here */
  </style>