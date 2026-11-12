<template>
  <footer class="ftr">
    <div class="container cols">
      <div>
        <brand-logo light />
        <p class="tag">{{ brand.tagline }}.</p>
        <p class="small">Un marketplace donde cada tienda vende con su propio medio de pago y atención directa.</p>
      </div>
      <div>
        <h4>Comprar</h4>
        <router-link to="/buscar?discounted=1&ordering=discount">Ofertas</router-link>
        <router-link to="/tiendas">Tiendas</router-link>
        <router-link to="/carrito">Mi carrito</router-link>
      </div>
      <div>
        <h4>Vender</h4>
        <router-link to="/registro">Registrar mi tienda</router-link>
        <router-link to="/ingresar">Ingresar al panel</router-link>
      </div>
      <div>
        <h4>Ayuda</h4>
        <router-link to="/ayuda">Preguntas frecuentes</router-link>
        <router-link to="/nosotros">¿Quiénes somos?</router-link>
        <router-link to="/terminos">Términos y condiciones</router-link>
        <a href="https://www.argentina.gob.ar/produccion/defensadelconsumidor" target="_blank" rel="noopener noreferrer">Defensa del Consumidor</a>
      </div>
    </div>
    <div class="legal">
      <div class="container">© {{ brand.year }} {{ brand.name }}. Todos los derechos reservados. Los pedidos se acuerdan directamente con cada tienda.</div>
    </div>
  </footer>
</template>

<script>
import { BRAND } from '@/brand';
import BrandLogo from './BrandLogo.vue';

export default { name: 'AppFooter', components: { BrandLogo }, data() { return { brand: BRAND }; } };
</script>

<style scoped>
.ftr { background: var(--brand-900); color: #c7d2fe; margin-top: 40px; }
.cols { display: grid; grid-template-columns: 1.6fr 1fr 1fr 1fr; gap: 28px; padding-top: 38px; padding-bottom: 28px; }
h4 { color: #fff; margin: 0 0 10px; font-size: .95rem; }
a { display: block; color: #c7d2fe; padding: 3px 0; }
a:hover { color: #fff; }
.tag { color: #fff; font-weight: 600; margin: 10px 0 4px; }
.legal { border-top: 1px solid rgba(255, 255, 255, .12); padding: 14px 0; font-size: .8rem; }
@media (max-width: 820px) { .cols { grid-template-columns: 1fr 1fr; } }
</style>
