# Plan de mejora del frontend + pagos

> **Estado (rama `rediseno`):** F0–F6 implementadas (identidad Multi-Market, sistema de diseño, portada, listado con filtros,
> ficha con galería, carrito lateral, checkout por pasos, seguimiento, páginas de tienda y panel). Pagos: Mercado Pago
> (marketplace, probado con respuestas simuladas, **pendiente de sandbox real**), transferencia, efectivo/retiro y link de pago.
> Pendiente: tests e2e automatizados y script `npm run screenshots` (F7), miniaturas de imágenes en el servidor, Ualá/MODO/PayPal por API.

Objetivo: que Multi-Market se vea y se sienta como un marketplace real (lo mejor de **Mercado Libre**, **Amazon** y **Tienda Nube**), con identidad propia (sin "Ciudad Oferta"), datos de demo atractivos para capturas del README y pagos online con **Mercado Pago** y otros medios.

## 0. Qué tomamos de cada referencia

| Referencia | Lo que copiamos (como idea, no el diseño) |
|---|---|
| **Mercado Libre** | Buscador protagonista en la cabecera; filtros laterales (precio, categoría, tienda, descuento, con stock); etiquetas "% OFF" y "Envío gratis"; precio con cuotas; botón **Comprar ahora**; breadcrumbs; tarjetas limpias sobre fondo claro. |
| **Amazon** | Menú de categorías siempre accesible; **Agregar al carrito** + mini-carrito lateral; checkout por pasos con resumen fijo; sección "Productos relacionados"; confianza (pago seguro, devoluciones) cerca del botón de compra. |
| **Tienda Nube** | **Página propia por tienda** (`/tienda/<slug>`) con logo, banner y catálogo; estética minimalista con mucho aire; panel del vendedor simple con wizard para cargar productos. |

## 1. Diagnóstico del front actual

- Estilos en un único `base.css` de 468 líneas, sin variables ni sistema de componentes; colores planos (verde fluo / gris) y tarjetas con huecos.
- Branding hardcodeado: "Ciudad Oferta" en `App.vue` y `TermsConditions.vue`, "MultiMercados" en el pie, logo `logo.jpeg`, título/favicon por defecto.
- Cabecera sin menú de categorías real; enlaces de soporte decorativos; sin estados de carga/vacío/error consistentes.
- Producto con **una sola imagen**; filtros del listado solo por precio; sin breadcrumbs ni relacionados.
- Checkout de una sola pantalla sin pago online (hoy se coordina por WhatsApp).

## 2. Fases del frontend

### F0 – Identidad (1 día)
- Nombre de marca único: **Multi-Market** (propuesta; ver preguntas).
- Logo demo propio en SVG (monograma "M" + bolsa de compras), variantes color/blanco, favicon y `<title>`.
- Reemplazar todas las apariciones de "Ciudad Oferta"/"MultiMercados" (cabecera, términos, pie, `public/index.html`) tomando el nombre desde una sola constante (`src/brand.js`).
- Paleta y tipografía: tokens CSS (`--color-primary`, `--radius`, `--shadow`…), claro/oscuro opcional.

### F1 – Sistema de diseño y layout (2 días)
- Variables CSS + componentes base: `AppHeader`, `AppFooter`, `ProductCard`, `PriceTag` (precio, tachado, % OFF, cuotas), `Badge`, `Button`, `Skeleton`, `EmptyState`, `Breadcrumbs`, `Pagination`.
- Cabecera tipo ML/Amazon: logo · buscador grande con sugerencias · cuenta · carrito con contador · barra de categorías desplegable.
- Responsive real (móvil primero), foco visible y contraste AA.

### F2 – Home (1–2 días)
- Hero/carrusel de banners por categoría; fila de categorías con íconos.
- "Ofertas del día" (mayor descuento) y carruseles por categoría.
- "Tiendas destacadas" con tarjeta de tienda (logo + cantidad de productos).
- Barra de confianza: pago seguro · tiendas verificadas · cuotas.

### F3 – Listado y búsqueda (2 días)
- Filtros laterales: categoría/subcategoría, rango de precio, tienda, con descuento, con stock; orden (relevancia, precio, descuento, novedad).
- Paginación **en servidor** (el backend ya la soporta), skeletons, "sin resultados" con sugerencias.
- Breadcrumbs y URL con los filtros (compartible).

### F4 – Ficha de producto (2 días)
- Galería con varias imágenes y zoom (nuevo modelo `ProductImage` en el backend).
- Bloque de compra: precio final, cuotas, stock, selector de cantidad, **Comprar ahora** y **Agregar al carrito**, tarjeta de la tienda, medios de pago aceptados.
- Productos relacionados (misma subcategoría) y "más de esta tienda".

### F5 – Carrito y checkout por pasos (2 días)
- Mini-carrito (drawer) al agregar; página de carrito completa.
- Checkout: **1. Datos → 2. Entrega → 3. Pago → 4. Confirmación**, con resumen fijo; un pedido por tienda (ver §4).
- Página de seguimiento del pedido (`/pedido/<id>?token=…`) sin necesidad de cuenta.

### F6 – Tiendas (Tienda Nube) (2 días)
- `slug`, logo, banner y descripción en el perfil de tienda; página `/tienda/<slug>`.
- Panel del vendedor: dashboard (ventas, pedidos pendientes, stock bajo), wizard de producto con arrastrar y soltar imágenes, **Conectar Mercado Pago**, configuración de medios de pago (transferencia, efectivo).

### F7 – Calidad y capturas (1 día)
- Carga diferida de rutas, miniaturas de imágenes (thumbnail en el backend), meta tags básicos.
- Tests e2e con Playwright (compra completa, panel vendedor) y **script reproducible de capturas** (`npm run screenshots`) que regenera las imágenes del README.

## 3. Datos y fotos de demo

- `seed_demo` ampliado: ~8 tiendas con logo/banner, 6–8 categorías y **40–60 productos** con 2–4 imágenes cada uno, descripciones, descuentos y stock realistas.
- Fotos: **opción recomendada**: fotos libres de licencia (Unsplash/Pexels) descargadas una vez a `backend/demo_assets/` con un archivo `CREDITS.md`; no se hotlinkea. **Alternativa** si no hay red o prefieres evitar terceros: ilustraciones de producto generadas con Pillow (menos realistas). Tú puedes además aportar tus propias fotos.
- Logo y banners de demo creados como SVG propios (sin marcas de terceros).

## 4. Pagos: arquitectura

**Principio**: el backend nunca confía en el navegador. El estado de pago se confirma consultando al proveedor, y los precios siguen calculándose en el servidor.

- Nueva app `payments`: modelo `Payment` (pedido, proveedor, estado `pending/approved/rejected/refunded`, `external_id`, monto, payload crudo) y una interfaz de proveedor (`create_checkout`, `handle_webhook`, `refund`) para poder sumar medios sin tocar el resto.
- `Order` gana `payment_status` y un `public_token` para el seguimiento sin cuenta.

### 4.1 Mercado Pago (principal)
- **Modelo marketplace**: cada tienda conecta su cuenta por **OAuth** (guardamos su `access_token`/`refresh_token` cifrados). Cada pedido crea una *preferencia de Checkout Pro* con el token del vendedor y una **comisión de la plataforma** (`marketplace_fee`, configurable; 0 en la demo).
- Webhook `POST /api/payments/mercadopago/webhook/`: valida la firma `x-signature`, **consulta el pago en la API de MP** (no usa el cuerpo recibido), es idempotente y actualiza el pedido.
- Retornos `success / pending / failure` hacia el front; cuotas, tarjetas, dinero en cuenta y QR vienen incluidos en Checkout Pro.
- Limitación: un pago de MP corresponde a **un solo vendedor**. Con un carrito de varias tiendas, el checkout paga **tienda por tienda** (se muestra como "Pedido 1 de 2…").
- Pruebas con credenciales y usuarios de **sandbox** de Mercado Pago.

### 4.2 Otros medios
- **Transferencia bancaria (CBU/alias)**: la tienda carga sus datos; el comprador sube el comprobante y la tienda marca "pago recibido".
- **Efectivo / retiro en local / contra entrega**: sin pasarela; la tienda confirma el cobro.
- **WhatsApp** (ya existe): coordinación manual como alternativa.
- **Opcionales, mismo patrón de proveedor**: Ualá Bis, MODO o PayPal (más útil para venta internacional). Stripe no se prioriza por disponibilidad limitada para comercios en Argentina.
- Cada tienda elige qué medios acepta; el checkout solo muestra los habilitados.

### 4.3 Seguridad y cumplimiento
- Tokens de vendedores cifrados y fuera de las respuestas de la API; secretos solo por variables de entorno (`MP_APP_ID`, `MP_CLIENT_SECRET`, `MP_WEBHOOK_SECRET`).
- Nunca se guardan datos de tarjeta (todo va por la pasarela).
- Tests con respuestas simuladas del proveedor (pago aprobado, rechazado, webhook repetido, firma inválida).
- Antes de cobrar dinero real: términos y condiciones, política de reembolsos y requisitos fiscales (facturación) revisados por el responsable del negocio.

## 5. Orden de trabajo sugerido

1. **F0 + F1** (identidad y sistema de diseño) → ya cambia por completo la cara del sitio.
2. **Datos y fotos de demo + F2/F3/F4** → capturas lindas para el README.
3. **Backend de pagos (transferencia/efectivo primero) + F5** → compra completa de punta a punta.
4. **Mercado Pago** (OAuth, preferencia, webhook) con sandbox.
5. **F6 y F7** → tiendas, panel y capturas automáticas.

Estimación total: ~3 semanas de trabajo; los puntos 1–2 dejan un front presentable en ~1 semana.

## 6. Preguntas abiertas

1. ¿Nombre de marca definitivo? (propuesta: **Multi-Market**)
2. ¿Tienes cuenta de Mercado Pago y una aplicación creada en el panel de desarrolladores? Para la integración real se necesitan sus credenciales de **prueba**.
3. ¿Qué medios además de Mercado Pago quieres en la primera versión? (propuesta: transferencia + efectivo/retiro)
4. ¿Comisión de la plataforma sobre cada venta? (propuesta: configurable, 0 % en la demo)
5. ¿Fotos de demo: descargar libres de licencia (recomendado) o generarlas con Pillow?
