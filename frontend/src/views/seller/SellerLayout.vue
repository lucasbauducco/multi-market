<template>
  <div class="container page">
    <div class="panel">
      <aside class="side card card-pad">
        <div class="me">
          <div class="av">{{ (razonSocial || '?').slice(0, 1) }}</div>
          <div><strong>{{ razonSocial || 'Mi tienda' }}</strong><div class="small muted">@{{ username }}</div></div>
        </div>
        <nav class="nav" aria-label="Panel de la tienda">
          <router-link v-for="l in links" :key="l.to" :to="l.to" class="lnk" exact-active-class="on" :class="{ on: isActive(l) }">
            <span>{{ l.icon }}</span>{{ l.label }}
          </router-link>
          <a v-if="slug" :href="`/tienda/${slug}`" class="lnk" @click.prevent="$router.push(`/tienda/${slug}`)"><span>👁️</span>Ver mi tienda</a>
          <button class="lnk out" @click="logout"><span>↩</span>Salir</button>
        </nav>
      </aside>
      <section class="content"><router-view /></section>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import api from '@/api';

export default {
  name: 'SellerLayout',
  data() {
    return {
      slug: '',
      links: [
        { to: '/panel', label: 'Resumen', icon: '📊', exact: true },
        { to: '/panel/productos', label: 'Productos', icon: '📦', prefix: '/panel/productos' },
        { to: '/panel/pedidos', label: 'Pedidos', icon: '🧾', prefix: '/panel/pedidos' },
        { to: '/panel/configuracion', label: 'Configuración y cobros', icon: '⚙️', prefix: '/panel/configuracion' },
      ],
    };
  },
  computed: { ...mapState(['razonSocial', 'username']) },
  methods: {
    isActive(l) { return l.exact ? this.$route.path === l.to : this.$route.path.startsWith(l.prefix); },
    async logout() {
      try { await api.post('/logout/'); } catch (e) { /* el token se descarta igual */ }
      await this.$store.dispatch('clearToken');
      this.$router.push('/');
    },
  },
  async mounted() {
    try { this.slug = (await api.get('/api/shop/profile/')).data.slug || ''; } catch (e) { /* sin slug */ }
  },
};
</script>

<style scoped>
.panel { display: grid; grid-template-columns: 250px 1fr; gap: 22px; align-items: start; }
.side { position: sticky; top: 130px; }
.me { display: flex; align-items: center; gap: 12px; padding-bottom: 14px; border-bottom: 1px solid var(--border); margin-bottom: 10px; }
.av { width: 44px; height: 44px; border-radius: 12px; background: var(--brand-600); color: #fff; display: grid; place-items: center; font-weight: 800; font-size: 1.2rem; }
.nav { display: flex; flex-direction: column; gap: 2px; }
.lnk { display: flex; gap: 10px; align-items: center; padding: 10px 12px; border-radius: 10px; color: #374151; font-weight: 600; background: none; border: 0; font: inherit; font-weight: 600; text-align: left; cursor: pointer; text-decoration: none !important; }
.lnk:hover { background: var(--brand-50); }
.lnk.on { background: var(--brand-50); color: var(--brand-700); }
.out { color: var(--bad); }
.content { min-width: 0; }
@media (max-width: 900px) {
  .panel { grid-template-columns: 1fr; }
  .side { position: static; }
  .nav { flex-direction: row; flex-wrap: wrap; }
}
</style>
