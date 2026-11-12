# Multi-Market

Marketplace donde varias tiendas publican sus productos y los clientes arman un carrito y envían pedidos a cada tienda (el pago y la entrega se coordinan con la tienda, p. ej. por WhatsApp).

- `backend/`: API Django REST (JWT/Token, SQLite por defecto).
- `frontend/`: SPA Vue 3 (vue-cli, vuex, vue-router).
- `docs/PLAN.md`: plan de mejoras y estado.

## Qué incluye

- Catálogo público: búsqueda paginada, categorías, ofertas, detalle de producto.
- Carrito y checkout sin cuenta; un pedido por tienda; precios y stock calculados en el servidor.
- Alta de tiendas (`/register`) con aprobación manual desde `/admin/`.
- Panel de la tienda: productos (con imagen), stock, descuentos y pedidos (confirmar / entregar / cancelar).

## Arranque local

Requisitos: Python 3.11+ y Node 18+.

```bash
# Backend (http://127.0.0.1:8000)
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo                              # datos de ejemplo (opcional)
python manage.py createsuperuser                        # para /admin/ (opcional)
python manage.py runserver

# Frontend (http://localhost:8081) en otra terminal
cd frontend
npm install
npm run serve
```

Tiendas de demo (tras `seed_demo`): `techzone`, `casabella`, `urbanstyle` — contraseña `demo12345`.
Login de tienda en `/login`. Si el backend corre en otra URL: `frontend/.env.development` → `VUE_APP_API_URL`.

Tests del backend: `cd backend && python manage.py test`.

## Configuración (variables de entorno del backend)

Ver `backend/.env.example`. Principales: `DJANGO_SECRET_KEY` (obligatoria con `DJANGO_DEBUG=False`),
`DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `DB_ENGINE`/`DB_*` (MySQL/Postgres), `SQLITE_PATH`.
MySQL: `pip install -r requirements-mysql.txt`.

## Despliegue con Docker

```bash
export DJANGO_SECRET_KEY="$(python -c 'import secrets;print(secrets.token_urlsafe(50))')"
docker compose up --build        # frontend en :8080, API en :8000
docker compose exec backend python manage.py createsuperuser
```

Para producción: poner `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` y `VUE_APP_API_URL` con tus dominios (HTTPS),
usar una base de datos gestionada y un almacenamiento externo para `media/`.

## Seguridad

Ya no hay credenciales en el repositorio. **La contraseña de MySQL y la `SECRET_KEY` anteriores quedaron en el
historial de Git: considerá rotarlas.**

## Licencia

Ver `LICENSE`.
