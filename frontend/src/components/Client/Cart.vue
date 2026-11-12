<template>
  <section class="cart">
    <h2>Tu carrito</h2>

    <div v-if="orders.length" class="done">
      <h3>¡Pedido enviado!</h3>
      <p>Cada tienda recibió tu pedido. Coordiná el pago y la entrega directamente con ellas:</p>
      <ul>
        <li v-for="o in orders" :key="o.id">
          <strong>{{ o.shop_name }}</strong> – pedido #{{ o.id }} – ${{ o.total }}
          <a v-if="o.shop_phone" :href="whatsappLink(o)" target="_blank" rel="noopener">Escribir por WhatsApp</a>
        </li>
      </ul>
      <router-link to="/">Seguir comprando</router-link>
    </div>

    <div v-else-if="!items.length" class="empty">
      <p>Tu carrito está vacío.</p>
      <router-link to="/search">Ver ofertas</router-link>
    </div>

    <div v-else class="cart-layout">
      <table class="cart-table">
        <thead><tr><th>Producto</th><th>Precio</th><th>Cant.</th><th>Subtotal</th><th></th></tr></thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>
              <router-link :to="{ name: 'ProductDetails', params: { productId: item.id } }">{{ item.name }}</router-link>
              <div class="muted">{{ item.shop_name }}</div>
            </td>
            <td>${{ item.price.toFixed(2) }}</td>
            <td>
              <input type="number" min="1" max="999" :value="item.quantity"
                     @change="setQuantity({ id: item.id, quantity: parseInt($event.target.value) || 1 })" />
            </td>
            <td>${{ (item.price * item.quantity).toFixed(2) }}</td>
            <td><button class="link" @click="removeFromCart(item.id)" aria-label="Quitar">✕</button></td>
          </tr>
        </tbody>
        <tfoot><tr><td colspan="3"><strong>Total</strong></td><td colspan="2"><strong>${{ cartTotal.toFixed(2) }}</strong></td></tr></tfoot>
      </table>

      <form class="checkout" @submit.prevent="submit">
        <h3>Tus datos</h3>
        <input v-model.trim="form.buyer_name" placeholder="Nombre y apellido" required maxlength="120" />
        <input v-model.trim="form.buyer_phone" placeholder="Teléfono / WhatsApp" required maxlength="40" />
        <input v-model.trim="form.buyer_email" type="email" placeholder="Email (opcional)" />
        <textarea v-model.trim="form.notes" placeholder="Notas para la tienda (opcional)" maxlength="500"></textarea>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="sending">{{ sending ? 'Enviando…' : 'Confirmar pedido' }}</button>
        <small class="muted">No se cobra nada online: la tienda te contacta para acordar pago y entrega.</small>
      </form>
    </div>
  </section>
</template>

<script>
import { mapActions, mapGetters, mapState } from 'vuex';
import api, { errorMessage } from '@/api';

export default {
  name: 'CartView',
  data() {
    return {
      form: { buyer_name: '', buyer_phone: '', buyer_email: '', notes: '' },
      sending: false,
      error: '',
      orders: [],
    };
  },
  computed: {
    ...mapState({ items: 'cart' }),
    ...mapGetters(['cartTotal']),
  },
  methods: {
    ...mapActions(['setQuantity', 'removeFromCart', 'clearCart']),
    async submit() {
      this.sending = true;
      this.error = '';
      try {
        const payload = {
          ...this.form,
          items: this.items.map(i => ({ product: i.id, quantity: i.quantity })),
        };
        const { data } = await api.post('/api/checkout/', payload);
        this.orders = data;
        this.clearCart();
      } catch (e) {
        this.error = errorMessage(e, 'No pudimos enviar el pedido.');
      } finally {
        this.sending = false;
      }
    },
    whatsappLink(order) {
      const lines = order.items.map(i => `${i.quantity} x ${i.name}`).join(', ');
      const text = `Hola! Hice el pedido #${order.id} en Multi-Market: ${lines}. Total $${order.total}.`;
      return `https://wa.me/${String(order.shop_phone).replace(/\D/g, '')}?text=${encodeURIComponent(text)}`;
    },
  },
};
</script>

<style scoped>
.cart { max-width: 1000px; margin: 2rem auto; padding: 0 1rem; }
.cart-layout { display: flex; gap: 2rem; flex-wrap: wrap; }
.cart-table { flex: 2 1 420px; border-collapse: collapse; }
.cart-table th, .cart-table td { padding: .6rem; border-bottom: 1px solid #ddd; text-align: left; }
.cart-table input { width: 4rem; }
.checkout { flex: 1 1 280px; display: flex; flex-direction: column; gap: .6rem; }
.checkout input, .checkout textarea { padding: .5rem; }
.muted { color: #666; font-size: .85rem; }
.error { color: #b00020; }
.link { background: none; border: none; cursor: pointer; color: #b00020; }
.done { background: #e8f5e9; padding: 1rem 1.5rem; border-radius: 8px; }
</style>
