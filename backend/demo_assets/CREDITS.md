# Créditos de las imágenes de demo

Las fotos de `images/` provienen de **[Unsplash](https://unsplash.com)** y se usan bajo la
[Licencia de Unsplash](https://unsplash.com/license): uso gratuito, incluso comercial, sin obligación de atribución
(agradecemos a los fotógrafos de la comunidad de Unsplash).

Cada archivo se llama como el identificador de la foto en Unsplash (`photo-<id>`), por ejemplo
`1511707171634-5f897ff02aa9.jpg` → `https://images.unsplash.com/photo-1511707171634-5f897ff02aa9`.
Fueron recortadas a 4:3 (productos) o a banner y reducidas a ~1000 px para la demo.

Los logos de las tiendas de demo se generan en `seed_demo` (monogramas propios) y el logo de Multi-Market es propio.

Los nombres de tiendas y productos son ficticios. Algunas fotos pueden mostrar objetos de marcas comerciales sin que
ello implique relación alguna con esas marcas.

Para reemplazar las fotos por las tuyas: copiá tus imágenes a `images/`, ajustá los nombres en `catalog.json` y ejecutá
`python manage.py seed_demo --reset`.
