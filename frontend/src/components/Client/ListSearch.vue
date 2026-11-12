<template>
    <div class="filter-container">
      <select v-model="selectedSort">
          <option value="lowerPrice">Menor Precio</option>
          <option value="higherPrice">Mayor Precio</option>
          <option value="bestDiscount">Mejor Descuento</option>
      </select>
      <input type="number" v-model="minPrice" placeholder="Precio Mínimo">
      <input type="number" v-model="maxPrice" placeholder="Precio Máximo">
      <button @click="applyFilters">Aplicar Filtros</button>
    </div>
    <div class="container-list">
      <div class="card" v-for="product in filteredProducts" :key="product.id">
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
          </div>
        </router-link>
        <div v-if="isAuthenticate && product.shop===shopId" class="btn-card">
            <button @click="editProduct(product.id)">Editar</button>
            <button @click="deleteProduct(product.id)">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
              </svg>
            </button>
          </div>
      </div>
    </div>
    <div class="pagination">
      <button @click="currentPage--" :disabled="currentPage <= 1" class="pagination-btn">Anterior</button>
      <!-- Numeración de la paginación -->
      <button v-for="page in paginationRange"
              @click="goToPage(page)"
              :disabled="currentPage === page"
              class="pagination-btn"
              :key="page">{{ page }}</button>
      
      <button @click="currentPage++" :disabled="currentPage >= maxPages" class="pagination-btn">Siguiente</button>
    </div>


  </template>
  
  <script>
 import axios from 'axios';
  export default {
    props: ['shopId', 'isAuthenticate'],
    data() {
      return {
        searchResults: [],
        filteredProducts: [], // directamente un arreglo, no un objeto
        selectedSort: 'bestDiscount', // Valor predeterminado del filtro de ordenamiento
        minPrice: null, // Valor predeterminado del precio mínimo
        maxPrice: Infinity, // Valor predeterminado del precio máximo
        currentPage: 1,
        productsPerPage: 20,
        maxPages: 1,
      };
    },
    created() {
    this.fetchSearchResults(this.$route.query.query);
  },
  watch: {
    // Observa cambios en la query de búsqueda
    '$route.query.query'(newQuery, oldQuery) {
      if (newQuery !== oldQuery) {
        this.fetchSearchResults(newQuery);
      }
    },
    // Observa cambios en la página actual
    'currentPage'(newValue, oldValue) {
      if (newValue !== oldValue) {
        this.applyFilters();
      }
    },
  },
  computed: {
    paginationRange() {
      let range = [];
      const totalPages = this.maxPages;
      const currentPage = this.currentPage;

      // Ejemplo simple de cómo podrías querer calcular 'start' y 'end'
      let start = currentPage - 2 > 0 ? currentPage - 2 : 1;
      let end = currentPage + 2 <= totalPages ? currentPage + 2 : totalPages;

      // Ajusta 'start' y 'end' según sea necesario para tu lógica específica

      for (let i = start; i <= end; i++) {
        range.push(i);
      }

      // Aquí puedes ajustar 'range' para incluir "..." o cualquier otra lógica

      return range;
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
    async fetchSearchResults(query) {
      const url = `http://localhost:8000/api/search_products/?query=${query}`; // Construir la URL

      try {
        const response = await fetch(url); // Realizar la solicitud al backendf
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`); // Manejar respuestas no exitosas
        }
        const data = await response.json(); // Parsear la respuesta JSON
        this.searchResults = data; // Actualizar el estado con los resultados
        await this.applyFilters();
      } catch (error) {
        console.error("Fetch error:", error); // Manejar errores en la solicitud
      }
    },
    filterAndSortResults() {
      let filteredResults = this.searchResults.products.filter(product => {
        const finalPrice = product.price - ((product.discount * product.price) / 100);
        // Considera 0 o null como valores no restrictivos
        const effectiveMinPrice = this.minPrice > 0 ? this.minPrice : 0;
        const effectiveMaxPrice = this.maxPrice > 0 ? this.maxPrice : Infinity;

        return finalPrice >= effectiveMinPrice && finalPrice <= effectiveMaxPrice;
      });

      switch(this.selectedSort) {
        case 'lowerPrice':
          filteredResults.sort((a, b) => (a.price - (a.discount * a.price / 100)) - (b.price - (b.discount * b.price / 100)));
          break;
        case 'higherPrice':
          filteredResults.sort((a, b) => (b.price - (b.discount * b.price / 100)) - (a.price - (a.discount * a.price / 100)));
          break;
        case 'bestDiscount':
          filteredResults.sort((a, b) => b.discount - a.discount);
          break;
      }

      return filteredResults;
    },
    applyFilters() {
      const filteredSortedResults = this.filterAndSortResults();
      this.filteredProducts = this.paginatedProducts(filteredSortedResults);
    },
    paginatedProducts(filteredSortedResults) {
      const start = (this.currentPage - 1) * this.productsPerPage;
      const end = start + this.productsPerPage;
      this.maxPages = Math.ceil(filteredSortedResults.length / this.productsPerPage);
      return filteredSortedResults.slice(start, end);
    },
    goToPage(page) {
      if (page) {
        this.currentPage = page;
        this.applyFilters();
      }
    },
  },
};
  </script>
  
<style>
.container-list {
    width: 100%;
    margin: 2rem 0;
    position: relative;
    justify-content: space-around;
    display: flex;
    flex-wrap: wrap;
}
.filter-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    gap: 10px;
    margin-bottom: 20px;
    background-color: #f8f9fa; /* Fondo claro para el contenedor de filtros */
    padding: 10px;
    border-radius: 5px;
}

.filter-container select, .filter-container input {
    padding: 8px 12px;
    border: 1px solid #ced4da; /* Borde suave */
    border-radius: 5px; /* Bordes redondeados para suavidad */
    font-size: 14px; /* Tamaño de texto adecuado */
    color: #495057; /* Color de texto */
    background-color: #ffffff; /* Fondo blanco para destacar */
}

.filter-container button {
    padding: 8px 16px;
    border: none;
    border-radius: 5px; /* Bordes redondeados para el botón */
    font-size: 14px; /* Tamaño de texto adecuado */
    color: #ffffff; /* Color de texto blanco */
    background-color: #007bff; /* Fondo azul, cambia esto según tu esquema de color */
    cursor: pointer; /* Cambiar el cursor a pointer */
    transition: background-color 0.2s; /* Transición suave al cambiar el color */
}

.filter-container button:hover {
    background-color: #0056b3; /* Color más oscuro al pasar el mouse */
}

/* Adicional: estilos para enfocar elementos con tabulación para accesibilidad */
.filter-container select:focus, .filter-container input:focus, .filter-container button:focus {
    outline: none;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25); /* Resplandor azul al enfocar */
}
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px; /* Espacio entre elementos */
  margin: 20px 0; /* Margen superior e inferior para separar de otros elementos */
}

.pagination-btn {
  background-color: #007bff; /* Color de fondo */
  border: none;
  border-radius: 5px; /* Bordes redondeados */
  color: white; /* Color del texto */
  padding: 10px 20px; /* Espaciado interno */
  cursor: pointer; /* Cambiar cursor a puntero */
  transition: background-color 0.3s; /* Transición suave al cambiar el color */
}

.pagination-btn:disabled {
  background-color: #ccc; /* Color de fondo para botón deshabilitado */
  cursor: not-allowed; /* Cambiar cursor a no permitido */
}

.pagination-btn:not(:disabled):hover {
  background-color: #0056b3; /* Color de fondo al pasar el mouse */
}

.pagination-status {
  font-size: 16px; /* Tamaño del texto */
}
</style>
  