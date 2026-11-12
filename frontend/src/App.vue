<template>
  <app-header />
  <main id="main">
    <router-view v-slot="{ Component, route }">
      <component :is="Component" :key="route.meta.keepKey ? route.meta.keepKey : route.path" />
    </router-view>
  </main>
  <app-footer />
  <cart-drawer />
</template>

<script>
import './styles/main.css';
import AppHeader from '@/components/layout/AppHeader.vue';
import AppFooter from '@/components/layout/AppFooter.vue';
import CartDrawer from '@/components/layout/CartDrawer.vue';

export default {
  name: 'App',
  components: { AppHeader, AppFooter, CartDrawer },
};
</script>

<style>
#main { min-height: 60vh; }
</style>
