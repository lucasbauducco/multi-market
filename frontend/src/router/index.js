// router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import store from '../store';

const Home = () => import('../views/HomeView.vue');
const Search = () => import('../views/SearchView.vue');
const Product = () => import('../views/ProductView.vue');
const Cart = () => import('../views/CartView.vue');
const Checkout = () => import('../views/CheckoutView.vue');
const Order = () => import('../views/OrderView.vue');
const ShopPage = () => import('../views/ShopPageView.vue');
const Shops = () => import('../views/ShopsView.vue');
const Login = () => import('../views/LoginView.vue');
const Register = () => import('../views/RegisterView.vue');
const StaticPage = () => import('../views/StaticPages.vue');
const NotFound = () => import('../views/NotFoundView.vue');
const SellerLayout = () => import('../views/seller/SellerLayout.vue');
const Dashboard = () => import('../views/seller/DashboardView.vue');
const SellerProducts = () => import('../views/seller/ProductsView.vue');
const ProductForm = () => import('../views/seller/ProductFormView.vue');
const SellerOrders = () => import('../views/seller/OrdersView.vue');
const Settings = () => import('../views/seller/SettingsView.vue');

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/buscar', name: 'Search', component: Search, meta: { keepKey: 'search' } },
  { path: '/producto/:id', name: 'Product', component: Product },
  { path: '/carrito', name: 'Cart', component: Cart },
  { path: '/checkout', name: 'Checkout', component: Checkout },
  { path: '/pedido/:token', name: 'Order', component: Order },
  { path: '/tiendas', name: 'Shops', component: Shops },
  { path: '/tienda/:slug', name: 'ShopPage', component: ShopPage },
  { path: '/ingresar', name: 'Login', component: Login },
  { path: '/registro', name: 'Register', component: Register },
  { path: '/nosotros', component: StaticPage, props: { kind: 'about' } },
  { path: '/ayuda', component: StaticPage, props: { kind: 'help' } },
  { path: '/terminos', component: StaticPage, props: { kind: 'terms' } },

  {
    path: '/panel',
    component: SellerLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Dashboard', component: Dashboard },
      { path: 'productos', component: SellerProducts },
      { path: 'productos/nuevo', component: ProductForm },
      { path: 'productos/:id', component: ProductForm },
      { path: 'pedidos', component: SellerOrders },
      { path: 'configuracion', component: Settings },
    ],
  },

  // Rutas antiguas -> nuevas
  { path: '/login', redirect: '/ingresar' },
  { path: '/register', redirect: '/registro' },
  { path: '/search', redirect: to => ({ path: '/buscar', query: to.query }) },
  { path: '/categories', redirect: '/buscar' },
  { path: '/product/:id', redirect: to => `/producto/${to.params.id}` },
  { path: '/cart', redirect: '/carrito' },
  { path: '/about-us', redirect: '/nosotros' },
  { path: '/help', redirect: '/ayuda' },
  { path: '/terms-conditions', redirect: '/terminos' },
  { path: '/shop/settings', redirect: to => ({ path: '/panel/configuracion', query: to.query }) },
  { path: '/shop/:rest(.*)*', redirect: '/panel' },

  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  scrollBehavior(to, from, saved) {
    if (saved) return saved;
    if (to.path === from.path) return false;
    return { top: 0 };
  },
});

router.beforeEach((to) => {
  if (to.matched.some(r => r.meta.requiresAuth) && !store.getters.isLoggedIn) {
    return { path: '/ingresar', query: { next: to.fullPath } };
  }
  return true;
});

export default router;
