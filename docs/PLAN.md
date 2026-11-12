# Plan de mejoras – Multi-Market (camino a MVP mostrable)

Estado de cada fase: [x] hecho · [ ] pendiente

## Fase 1 – Seguridad y configuración (backend)
- [x] Configuración por variables de entorno (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, CORS, base de datos). SQLite por defecto, MySQL/Postgres opcional.
- [x] Cerrar edición/borrado de productos sin autenticación y validar que el producto sea de la tienda.
- [x] `shop` no editable por el cliente; borrar `.pyc` del repo, `.gitignore`, `requirements.txt` en UTF-8.
- [x] Arreglar endpoints rotos (`ShopCategoriesAPIView`, `CustomUserDetailView`, `ShopProductsListView`) y rutas duplicadas.
- [x] Listados públicos solo con productos activos.

## Fase 2 – Funcionalidad de marketplace (backend)
- [x] Alta pública de tiendas (`/api/register/`), activación manual por el admin.
- [x] Imágenes como archivos (`ImageField`) en vez de base64 en la base de datos.
- [x] Stock opcional por producto.
- [x] Pedidos: carrito → pedido (uno por tienda), estados, listado para la tienda, enlace a WhatsApp.
- [x] Búsqueda paginada.
- [x] Comando `seed_demo` con datos de ejemplo.
- [x] Tests automatizados (permisos, registro, pedidos, búsqueda).

## Fase 3 – Frontend
- [x] URL de la API por variable de entorno (`VUE_APP_API_URL`), cliente axios único con token.
- [x] Carrito (persistente) y checkout.
- [x] Registro de tienda y panel de pedidos de la tienda.
- [x] Mostrar imágenes por URL, limpieza de código sobrante.

## Fase 4 – Despliegue y documentación
- [x] Dockerfile backend + docker-compose (backend + frontend estático).
- [x] README con arranque local en 3 comandos y guía de despliegue.

## Fuera de alcance (siguiente etapa)
- Pagos online (Mercado Pago), envíos, reseñas, notificaciones por email, panel de administración propio.
