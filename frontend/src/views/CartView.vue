<template>
  <div class="container page">
    <h1>Tu carrito</h1>
    <empty-state v-if="!groups.length" icon="🛒" title="Tu carrito está vacío" text="Agregá productos de una o varias tiendas y comprá todo junto." to="/buscar" cta="Explorar productos" />

    <div v-else class="layout">
      <section class="stack">
        <article v-for="g in groups" :key="g.shop" class="card">
          <header class="ghead">
            <router-link v-if="g.shop_slug" :to="`/tienda/${g.shop_slug}`"><strong>🏪 {{ g.shop_name }}</strong></router-link>
            <strong v-else>🏪 {{ g.shop_name }}</strong>
            <span class="muted small">Se genera un pedido para esta tienda</span>
          </header>
          <div v-for="i in g.items" :key="i.id" class="line">
            <img v-if="i.image" :src="i.image" :alt="i.name" />
            <div v-else class="ph"></div>
            <div class="info">
              <router-link :to="`/producto/${i.id}`" class="name">{{ i.name }}</router-link>
              <span class="muted small">{{ money(i.price) }} c/u</span>
              <button class="btn-link small rm" @click="removeFromCart(i.id)">Quitar</button>
            </div>
            <div class="qty">
              <button aria-label="Menos" :disabled="i.quantity <= 1" @click="setQuantity({ id: i.id, quantity: i.quantity - 1 })">−</button>
              <span>{{ i.quantity }}</span>
              <button aria-label="Más" @click="setQuantity({ id: i.id, quantity: i.quantity + 1 })">+</button>
            </div>
            <strong class="sub">{{ money(i.price * i.quantity) }}</strong>
          </div>
          <footer class="gfoot"><span>Subtotal tienda</span><strong>{{ money(g.total) }}</strong></footer>
        </article>
      </section>

      <aside class="summary card card-pad">
        <h2>Resumen</h2>
        <div class="srow"><span>Productos ({{ cartCount }})</span><span>{{ money(cartTotal) }}</span></div>
        <div class="srow muted small"><span>Envío</span><span>Se acuerda con cada tienda</span></div>
        <div class="srow total"><span>Total</span><strong>{{ money(cartTotal) }}</strong></div>
        <router-link to="/checkout" class="btn btn-accent btn-lg btn-block">Continuar compra</router-link>
        <router-link to="/buscar" class="btn btn-ghost btn-block">Seguir comprando</router-link>
        <p v-if="groups.length > 1" class="alert alert-info small">Tu compra incluye {{ groups.length }} tiendas: pagás cada pedido por separado.</p>
      </aside>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapState } from 'vuex';
import EmptyState from '@/components/ui/EmptyState.vue';
import { money } from '@/utils';

export default {
  name: 'CartView',
  components: { EmptyState },
  computed: {
    ...mapState(['cart']),
    ...mapGetters(['cartCount', 'cartTotal', 'cartByShop']),
    groups() { return this.cartByShop; },
  },
  methods: { ...mapActions(['setQuantity', 'removeFromCart']), money },
  mounted() { document.title = 'Carrito – Multi-Market'; },
};
</script>

<style scoped>
.layout { display: grid; grid-template-columns: 1fr 340px; gap: 20px; align-items: start; margin-top: 12px; }
.ghead { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--border); background: #fafbff; border-radius: var(--radius) var(--radius) 0 0; flex-wrap: wrap; gap: 6px; }
.line { display: grid; grid-template-columns: 76px 1fr auto 110px; gap: 14px; align-items: center; padding: 14px 16px; border-bottom: 1px solid var(--border); }
.line img, .ph { width: 76px; height: 76px; border-radius: 10px; object-fit: cover; background: #eef0f7; }
.info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.name { color: var(--text); font-weight: 600; }
.rm { align-self: flex-start; color: var(--bad); }
.qty { display: inline-flex; align-items: center; border: 1px solid #cfd3e2; border-radius: 10px; overflow: hidden; }
.qty button { width: 32px; height: 34px; border: 0; background: #f4f5fa; cursor: pointer; }
.qty span { min-width: 36px; text-align: center; font-weight: 600; }
.sub { text-align: right; }
.gfoot { display: flex; justify-content: space-between; padding: 12px 16px; }
.summary { position: sticky; top: 130px; display: flex; flex-direction: column; gap: 10px; }
.summary h2 { margin: 0; }
.srow { display: flex; justify-content: space-between; gap: 8px; }
.total { font-size: 1.25rem; border-top: 1px solid var(--border); padding-top: 12px; margin-top: 4px; }
@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
  .summary { position: static; }
  .line { grid-template-columns: 64px 1fr; }
  .line .qty, .line .sub { grid-column: 2; justify-self: start; }
}
</style>
