<template>
    <div class="product-details">
        <div class="product-image">
            <img :src="product.image || defaultImage" alt="Imagen del producto">
        </div>
        <div class="product-info">
          <h2 class="product-name">{{ product.name }}</h2>
            <div class="product-price" v-if="product.discount!=0">
                  <div class="card-discount">Descuento: - {{ product.discount }}%</div>
                  <div class="card-price cross-out">Precio: ${{ product.price }}</div>
                  <div class="card-price">Precio: ${{ product.price - ((product.discount * product.price) / 100 )}}</div>
            </div>
            <div class="product-price card-price" v-else >Precio: ${{ product.price }}</div>
            <div class="product-stock" v-if="product.stock !== null && product.stock !== undefined">
              {{ product.stock > 0 ? `Stock: ${product.stock}` : 'Sin stock' }}
            </div>
            <div class="add-cart">
              <input type="number" min="1" :max="product.stock || 999" v-model.number="quantity" />
              <button :disabled="product.stock === 0" @click="addToCart">Agregar al carrito</button>
              <span v-if="added" class="added">Agregado ✔ <router-link to="/cart">Ver carrito</router-link></span>
            </div>
            <div class="product-description">
              <span>Descripción:</span>
              {{ product.description  }}
            </div>
            <div class="shop-info">
              <span>Contacto</span>
              <div>
                {{ shop.razon_social }}
              </div>
              <div>
                <button v-if="shop.telefono" @click="contactarWhatsApp(shop.telefono)">Contactar por WhatsApp</button>
              </div>
              <a :href="`mailto:${shop.email}`">
                <img :src="emailIconPath" alt="go to email">
              </a>
              <div>
                <router-link
                  :to="{ name: 'ListSearch', query: { query: shop.razon_social } }"
                  
                >
                  ver más productos del venderdor
                </router-link>
              </div>
            </div>
            <!-- Datos del vendedor y más información aquí -->
        </div>
    </div>
  </template>
  
  <script>
  import api from '@/api';
  import defaultImage from '@/assets/image/product/noImage.png';
  export default {
    props: ['productId'],
    data() {
      return {
        emailIconPath: require('@/assets/svg/email_black_24dp.svg'),
        shop: {},
        quantity: 1,
        added: false,
        product: {
            image: defaultImage,
        }
        // Aquí iría la lógica para obtener los detalles del producto utilizando el productId
      };
    },
    methods: {
      addToCart() {
        const qty = Math.max(1, parseInt(this.quantity) || 1);
        this.$store.dispatch('addToCart', {
          id: this.product.id,
          name: this.product.name,
          price: parseFloat(this.product.final_price),
          image: this.product.image,
          shop_name: this.shop.razon_social || this.product.shop_name,
          quantity: qty,
        });
        this.added = true;
      },
      contactarWhatsApp(numero) {
        if (!numero) return;
        const urlWhatsApp = `https://wa.me/${String(numero).replace(/\D/g, '')}`;
        // Redirige al usuario a la URL
        window.open(urlWhatsApp, '_blank');
      },
      viewproductshop() {
        // Navega a ProductShop pasando el shop_id como parámetro
        this.$router.push({ name: 'ProductShop', params: { shop_id: this.shop.id } });
      },
      async fetchProductDetails() {
        const productId = this.$route.params.productId; // Asumiendo que estás usando vue-router
        await api.get(`/api/product/${productId}/`)
          .then(async response => {
            this.product = response.data;
            await api.get(`/api/product/${productId}/shop/`)  // Ajusta la URL según tu configuración de URL
              .then(response => {
                this.shop = response.data;  // Guarda la información del shop
              })
              .catch(error => {
                console.error("Error al obtener los detalles del producto:", error);
              });
            // Si tu API no devuelve una imagen en base64 y en su lugar devuelve una URL, ajusta la asignación aquí
          })
          .catch(error => {
            console.error("Error al obtener los detalles del producto:", error);
          });
      }
    },
    mounted() {
      this.fetchProductDetails();
    }
  }
  </script>
  
  <style>
.product-details {
  display: flex;
  flex-direction: row;
  margin: 4rem;
  justify-content: center;
  align-items: center;
  background-color: aliceblue;
}
.product-image {
  width: 60%;
  display: flex; 
  justify-content: center; 
  align-items: center; 
  margin: 1rem;
}
.product-image img{
  width: 100%;
  max-width: 500px; 
  height: auto; 
}

.product-info {
  margin: 1rem;
  padding: 2rem;
  background-color: #fff; /* Fondo claro */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Sombra suave */
  border-radius: 8px; /* Bordes suavizados */
  display: flex;
  flex-direction: column;
}
.product-name {
  font-size: 2rem; /* Nombre del producto más grande */
  margin-bottom: 1rem;
  color: #333; /* Color oscuro para mayor contraste */
}
.product-price{
  margin-top: 1rem;
}
.card-price {
  font-weight: bold; /* Precio más destacado */
}
.product-description{
  margin-top: 2rem;
  line-height: 1.5; /* Mejorar la legibilidad */
}
.shop-info {
  display: flex;
  flex-direction: column;
  gap: 10px; /* Ajusta el espacio entre los elementos */
}

.shop-info > span {
  font-weight: bold;
  margin-bottom: 5px;
}

.shop-info div,
.shop-info a {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 10px; /* Espacio entre el icono de email y el texto, si lo hay */
}

.router-link {
  display: inline-block;
  background-color: #007BFF; /* Color de fondo del enlace */
  color: white; /* Color del texto */
  padding: 10px 15px;
  border-radius: 5px; /* Bordes redondeados */
  text-decoration: none; /* Remueve el subrayado */
  transition: background-color 0.3s ease; /* Transición suave al cambiar de color */
}

.router-link:hover {
  background-color: #0056b3; /* Color al pasar el mouse */
}

.shop-info button {
  background-color: #28a745; /* Color de fondo del botón */
  color: white; /* Color del texto */
  border: none;
  padding: 10px 15px;
  border-radius: 5px; /* Bordes redondeados */
  cursor: pointer;
  transition: background-color 0.3s ease; /* Transición suave al cambiar de color */
}

.shop-info button:hover {
  background-color: #218838; /* Color al pasar el mouse */
}
@media screen and (max-width: 768px) {
  .product-details{
    flex-direction: column;
  }
  .product-info{
    margin-top: 2rem;
  }
}
  </style>
  