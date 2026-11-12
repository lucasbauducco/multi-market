<template>
  <div v-if="open" class="overlay" @click.self="close">
    <aside class="drawer" role="dialog" aria-modal="true" aria-label="Carrito">
      <header class="head">
        <h2>Tu carrito <span class="muted small">({{ cartCount }})</span></h2>
        <button class="x" aria-label="Cerrar" @click="close">✕</button>
      </header>

      <div v-if="!items.length" class="empty">
        <div class="big">🛒</div>
        <p>Tu carrito está vacío.</p>
        <button class="btn" @click="go('/buscar')">Explorar productos</button>
      </div>

      <template v-else>
        <ul class="list">
          <li v-for="i in items" :key="i.id" class="line">
            <img v-if="i.image" :src="i.image" :alt="i.name" />
            <div v-else class="ph"></div>
            <div class="info">
              <router-link :to="`/producto/${i.id}`" @click="close">{{ i.name }}</router-link>
              <span class="muted small">{{ i.shop_name }}</span>
              <div class="qty">
                <button aria-label="Menos" @click="setQuantity({ id: i.id, quantity: i.quantity - 1 })" :disabled="i.quantity <= 1">−</button>
                <span>{{ i.quantity }}</span>
                <button aria-label="Más" @click="setQuantity({ id: i.id, quantity: i.quantity + 1 })">+</button>
              </div>
            </div>
            <div class="side">
              <strong>{{ money(i.price * i.quantity) }}</strong>
              <button class="btn-link small" @click="removeFromCart(i.id)">Quitar</button>
            </div>
          </li>
        </ul>
        <footer class="foot">
          <div class="total"><span>Total</span><strong>{{ money(cartTotal) }}</strong></div>
          <button class="btn btn-accent btn-block btn-lg" @click="go('/checkout')">Finalizar compra</button>
          <button class="btn btn-ghost btn-block" @click="go('/carrito')">Ver carrito completo</button>
        </footer>
      </template>
    </aside>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapState } from 'vuex';
import { money } from '@/utils';

export default {
  name: 'CartDrawer',
  computed: {
    ...mapState({ items: 'cart', open: 'drawerOpen' }),
    ...mapGetters(['cartCount', 'cartTotal']),
  },
  watch: {
    open(v) { document.body.style.overflow = v ? 'hidden' : ''; },
    '$route.fullPath'() { this.close(); },
  },
  methods: {
    ...mapActions(['setQuantity', 'removeFromCart']),
    money,
    close() { this.$store.commit('CLOSE_DRAWER'); },
    go(path) { this.close(); this.$router.push(path); },
  },
};
</script>

<style scoped>
.overlay { position: fixed; inset: 0; background: rgba(15, 18, 40, .5); z-index: 100; display: flex; justify-content: flex-end; }
.drawer { width: min(420px, 100%); height: 100%; background: #fff; display: flex; flex-direction: column; box-shadow: var(--shadow-lg); animation: slide .2s ease-out; }
@keyframes slide { from { transform: translateX(40px); opacity: 0; } }
.head { display: flex; justify-content: space-between; align-items: center; padding: 16px 18px; border-bottom: 1px solid var(--border); }
.head h2 { margin: 0; }
.x { border: 0; background: none; font-size: 1.2rem; cursor: pointer; }
.empty { margin: auto; text-align: center; padding: 24px; }
.big { font-size: 3rem; }
.list { list-style: none; margin: 0; padding: 8px 18px; overflow: auto; flex: 1; }
.line { display: grid; grid-template-columns: 64px 1fr auto; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--border); }
.line img, .ph { width: 64px; height: 64px; border-radius: 10px; object-fit: cover; background: #eef0f7; }
.info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.info a { color: var(--text); font-weight: 600; line-height: 1.25; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.qty { display: inline-flex; align-items: center; gap: 4px; margin-top: 6px; }
.qty button { width: 26px; height: 26px; border-radius: 8px; border: 1px solid var(--border); background: #fff; cursor: pointer; }
.qty span { min-width: 24px; text-align: center; font-weight: 600; }
.side { display: flex; flex-direction: column; align-items: flex-end; justify-content: space-between; }
.foot { padding: 16px 18px; border-top: 1px solid var(--border); display: flex; flex-direction: column; gap: 10px; }
.total { display: flex; justify-content: space-between; font-size: 1.15rem; }
</style>
