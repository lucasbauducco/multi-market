<template>
  <div class="container page prose">
    <div class="card card-pad">
      <template v-if="kind === 'about'">
        <h1>¿Quiénes somos?</h1>
        <p><strong>Multi-Market</strong> es un marketplace que reúne a comercios de tu zona en un solo lugar. Cada tienda administra su catálogo, sus precios y sus medios de pago; vos comprás de varias tiendas con un único carrito.</p>
        <h2>Cómo funciona</h2>
        <ol>
          <li>Elegís productos de una o varias tiendas.</li>
          <li>Confirmás tus datos y elegís cómo pagar cada pedido: Mercado Pago, transferencia, efectivo/retiro o el link de pago de la tienda.</li>
          <li>Seguís el estado del pedido desde un enlace, sin necesidad de crear una cuenta.</li>
        </ol>
        <p>¿Tenés un comercio? <router-link to="/registro">Registrá tu tienda</router-link>.</p>
      </template>

      <template v-else-if="kind === 'help'">
        <h1>Preguntas frecuentes</h1>
        <details v-for="f in faq" :key="f.q"><summary>{{ f.q }}</summary><p>{{ f.a }}</p></details>
      </template>

      <template v-else>
        <h1>Términos y condiciones</h1>
        <p class="muted small">Última actualización: {{ year }}. Texto de ejemplo para la demo: debe ser revisado por el responsable legal del negocio antes de operar.</p>
        <h2>1. Rol de la plataforma</h2>
        <p><strong>Multi-Market</strong> provee un espacio donde comercios independientes publican y venden sus productos. La compraventa se celebra entre el comprador y cada tienda; la plataforma no es parte del contrato de venta.</p>
        <h2>2. Precios, stock y pedidos</h2>
        <p>Los precios y el stock son informados por cada tienda. Al confirmar, se genera un pedido por tienda, sujeto a su confirmación.</p>
        <h2>3. Pagos</h2>
        <p>Los pagos con Mercado Pago se procesan en la pasarela del proveedor; Multi-Market no almacena datos de tarjetas. Las transferencias, pagos en efectivo y enlaces de pago se acuerdan directamente con la tienda.</p>
        <h2>4. Entrega, cambios y devoluciones</h2>
        <p>La entrega y las políticas de cambio o devolución las define cada tienda, respetando la normativa vigente de defensa del consumidor.</p>
        <h2>5. Datos personales</h2>
        <p>Usamos tus datos únicamente para gestionar el pedido y comunicarlo a la tienda correspondiente.</p>
      </template>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StaticPage',
  props: { kind: { type: String, default: 'about' } },
  data() {
    return {
      year: new Date().getFullYear(),
      faq: [
        { q: '¿Necesito una cuenta para comprar?', a: 'No. Cargás tus datos al finalizar la compra y recibís un enlace para seguir tu pedido.' },
        { q: '¿Cómo pago?', a: 'Cada tienda habilita sus medios: Mercado Pago (tarjetas, dinero en cuenta, QR), transferencia bancaria, efectivo/retiro en local o un link de pago propio.' },
        { q: '¿Por qué recibo varios pedidos?', a: 'Se crea un pedido por tienda para que cada una gestione su pago y entrega. Podés pagarlos por separado.' },
        { q: '¿Cómo envío el comprobante de una transferencia?', a: 'Desde la página de tu pedido hay un botón para subir la captura. La tienda lo revisa y confirma el pago.' },
        { q: '¿Cómo vendo en Multi-Market?', a: 'Registrá tu tienda; después de la revisión podrás cargar productos, configurar tus medios de pago y recibir pedidos desde tu panel.' },
        { q: '¿Y si tengo un problema con mi pedido?', a: 'Escribile a la tienda por WhatsApp desde la página del pedido. También podés acudir a Defensa del Consumidor.' },
      ],
    };
  },
  mounted() { document.title = 'Multi-Market'; },
};
</script>

<style scoped>
.prose { max-width: 820px; }
.prose h2 { margin-top: 1.4em; }
details { border-bottom: 1px solid var(--border); padding: 12px 0; }
summary { cursor: pointer; font-weight: 700; }
details p { margin: 8px 0 0; color: #4b5563; }
</style>
