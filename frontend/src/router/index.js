// router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import Shop from '../views/Shop/HomeShop.vue';
import Login from '../components/Shop/LoginView.vue';
import Home from '../views/Client/Home.vue'
import Offers from '../components/Shop/Offers.vue';
import Categories from '../components/Client/Categories.vue';
import Sell from '../components/Shop/Sell.vue';
import ProductUpdate from '../components/Shop/ProductUpdate.vue';
import ProductDetails from '../components/ProductDetails.vue';
import store from '../store';
import ListSearch from '../components/Client/ListSearch';
import ListCategories from '../components/Client/ListCategories'
import NotFound from '../components/Error/NotFound.vue';
import ProductShop from '../components/Client/ListSearch.vue'
import AboutUs from '../components/Client/AboutUs.vue'
import TermsConditions from '../components/TermsConditions.vue'
import Help from '../components/Help.vue'

const routes = [
{
    path: '/',
    name: 'Home',
    component: Home,
    children: [
      {
        path: '/', // Esto se convertirá en /shop/products
        components: {
          offers: Offers,
        },
      },
    ],
  },
  {
    path: '/product/:productId',
    name: 'ProductDetails',
    component: ProductDetails,
    props: true,
  },
  {
    path: '/search',
    name: 'ListSearch',
    component: ListSearch,
    props: false
  },
  {
    path: '/about-us',
    name: 'AboutUs',
    component: AboutUs,
  },
  {
    path: '/terms-conditions',
    name: 'TermsConditions',
    component: TermsConditions,
  },
  {
    path: '/help',
    name: 'Help',
    component: Help,
  },
  {
    path: '/categories',
    name: 'ListCategories',
    component: ListCategories,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/shop',
    name: 'shop',
    component: Shop,
    children: [
      {
        path: 'products', // Esto se convertirá en /shop/products
        components: {
          offers: Offers,
          categories: Categories, // Asumiendo que puedas mostrar ambos en la misma ruta usando named views o similar
        },
        meta: { requiresAuth: true },
      },
      
      { path: '/product/update/:id', component: ProductUpdate , meta: { requiresAuth: true }},
      {
        path: 'sell', // Esto se convertirá en /shop/sell
        component: Sell,
        meta: { requiresAuth: true },
      },
      {
        path: '/mycity',
        name: 'ShopSearch',
        component: ListSearch,
        props: route => ({ shopId: route.query.shopId, isAuthenticate: route.query.isAuthenticate })
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*', // Ruta comodín para manejar cualquier ruta no encontrada
    name: 'NotFound',
    component: NotFound,
  },
  {
    path: '/shop/:shop_id/products',
    name: 'ProductShop',
    component: ProductShop,
    props: true // Habilita el paso de parámetros como props al componente
  },
  // otras rutas...
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!store.getters.isLoggedIn) {
      next({ name: 'Login' });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;