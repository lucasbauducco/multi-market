<template>
    <section class="createProduct">
        <section class="form">
            <form @submit.prevent="submitProduct">
                <div>
                    <label for="name">Nombre del producto:</label>
                    <input id="name" v-model="product.name" required>
                </div>
                <div>
                    <label for="description">Descripción:</label>
                    <textarea id="description" v-model="product.description" required></textarea>
                </div>
                <div>
                    <label for="price">Precio:</label>
                    <input id="price" type="number" step="0.01" v-model.number="product.price" required>
                </div>
                <div>
                    <label for="barcode">Código de barras:</label>
                    <input id="barcode" v-model="product.barcode" required>
                </div>
                <div>
                    <label for="discount">Descuento:</label>
                    <input id="discount" type="number" step="0.01" v-model.number="product.discount">
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
                <div>
                    <label for="image">Imagen (base64):</label>
                    <input id="image" type="file" @change="handleFileUpload">
                </div>
                <button type="submit">Enviar</button>
            </form>
        </section>
        <div class="card" :key="product.id">
            <img :src="product.image_base64" alt="Imagen del producto" class="card-image">
            <div class="card-body">
            <h3 class="card-title">{{ product.name }}</h3>
            <p class="card-description">{{ product.description }}</p>
            <div class="card-discount">Descuento: - {{ product.discount }}%</div>
            <div class="card-price">Precio: ${{ product.price }}</div>
            <!-- Otros detalles del producto -->
            </div>
        </div>
    </section>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: 'SellShop',
    props: ['shopId'],
    data() {
      return {
        product: {
            shop: this.shopId || null,
            name: '',
            description: '',
            price: 0,
            barcode: '',
            discount: 0,
            subcategory: null,
            image_base64: '',
        },
        subcategories: [],
        searchQuery: '',
        filteredSubcategories: [],
      };
    },
    mounted() {
        this.fetchSubcategories();
    },
    methods: {
        filterOptions() {
            if (this.searchQuery) {
                this.filteredSubcategories = this.subcategories.filter((subcat) =>
                subcat.name.toLowerCase().includes(this.searchQuery.toLowerCase())
                );
            } else {
                this.filteredSubcategories = this.subcategories;
            }
        },
        fetchSubcategories() {
            axios.get('http://127.0.0.1:8000/api/subcategories/')
                .then(response => {
                this.subcategories = response.data;
                })
                .catch(error => {
                console.error('Hubo un error al cargar las subcategorías:', error);
                });
        },
        handleFileUpload(event) {
            const file = event.target.files[0];
            if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                this.product.image_base64 = e.target.result;
            };
            reader.readAsDataURL(file);
            }
        },
        submitProduct() {
            // Obtiene el token desde el estado global (Vuex Store)
            const token = this.$store.state.token;
            // Configura las cabeceras de la solicitud
            const config = {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${token}` // Usa 'Bearer' en lugar de 'Token' si es el esquema esperado por tu backend
                }
            };
            const productData = this.product;
            // Realiza la solicitud POST con Axios
            axios.post('http://127.0.0.1:8000/api/products/', productData, config)
            .then(response => {
                alert('Producto creado con éxito', response);
                // Opcional: redirigir o limpiar el formulario aquí
            })
            .catch(error => {
                console.error(error);
                alert('Ocurrió un error al crear el producto');
            });
        },
    },
  };
</script>
<style>
.createProduct {
    display: flex;
    flex-direction: column; /* Cambiado a columna para mejor adaptabilidad */
    align-items: center;
    justify-content: center;
    padding: 20px;
    gap: 20px; /* Espacio entre los elementos */
}

/* Estilos para el formulario */
.createProduct .form {
    background-color: #f7f7f7;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    width: calc(100% - 40px);
    max-width: 500px;
}

.createProduct form > div {
    margin-bottom: 15px;
}

.createProduct label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

.createProduct input[type="number"],
.createProduct input[type="text"],
.createProduct input[type="file"],
.createProduct textarea,
.createProduct select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ced4da;
    border-radius: 5px;
    box-sizing: border-box;
}

.createProduct textarea {
    resize: vertical;
}

.createProduct button[type="submit"] {
    background-color: #007bff;
    color: #ffffff;
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.createProduct button[type="submit"]:hover {
    background-color: #0056b3;
}

/* Estilos para la vista previa del producto */
.createProduct .card {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    text-align: center;
    width: calc(100% - 30px); /* Ajuste de ancho con padding */
    max-width: 300px;
}

.createProduct .card-image {
    max-width: 100%;
    height: auto;
    border-radius: 5px;
    margin-bottom: 15px;
}

.createProduct .card-title,
.createProduct .card-description,
.createProduct .card-price,
.createProduct .card-discount {
    margin-bottom: 10px;
}

/* Media queries para responsividad */
@media (min-width: 768px) { /* Tablets y arriba */
    .createProduct {
        flex-direction: row; /* Cambio a fila para más espacio */
        gap: 40px;
    }

    .createProduct .form, .createProduct .card {
        max-width: none;
    }
}

@media (min-width: 1024px) { /* Desktops */
    .createProduct .form, .createProduct .card {
        max-width: 500px;
    }
}

</style>