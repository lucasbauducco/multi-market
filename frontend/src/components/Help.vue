<template>
    <div class="help-container">
      <h1>Centro de Ayuda</h1>
  
      <section>
        <h2>¿Cómo comprar productos?</h2>
        <p>Para realizar una compra en <strong>[Nombre de la Página Web]</strong>, sigue estos pasos:</p>
        <ol>
          <li>Navega por la categoría de productos o utiliza la barra de búsqueda para encontrar lo que deseas.</li>
          <li>Selecciona el producto que te interesa para ver más detalles.</li>
          <li>Si decides comprarlo, haz clic en el botón "Añadir al carrito".</li>
          <li>Revisa tu carrito y haz clic en "Proceder al pago".</li>
          <li>Completa la información de envío y pago y confirma tu compra.</li>
        </ol>
      </section>
  
      <section>
        <h2>¿Qué hacer en caso de problemas con tu compra?</h2>
        <p>Si encuentras algún problema con tu compra, como un producto defectuoso o un envío incorrecto, sigue estos pasos:</p>
        <ol>
          <li>Contacta directamente al vendedor a través de los detalles proporcionados en la página de información del producto.</li>
          <li>Si no recibes respuesta del vendedor, puedes contactar con nuestro soporte al cliente a través de <strong>[Correo de Soporte]</strong>.</li>
          <li>Proporciona todos los detalles necesarios como el número de pedido, la descripción del problema, y cualquier otra información relevante para ayudarte mejor.</li>
        </ol>
      </section>
  
      <section>
        <h2>Otras preguntas frecuentes</h2>
        <p>Si tienes otras dudas o necesitas más información, puedes consultar nuestras <a href="/faq">Preguntas Frecuentes</a> o contactar con nuestro soporte al cliente.</p>
      </section>
    </div>
  </template>
  
  <script>
  export default {
    name: 'HelpPage'
  }
  </script>
  
  <style scoped>
  .help-container {
    padding: 20px;
    margin: 1rem;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  
  .help-container h1, .help-container h2 {
    color: #2c3e50;
  }
  
  .help-container p, .help-container ol {
    color: #34495e;
    line-height: 1.6;
  }
  
  .help-container ol {
    margin-left: 20px;
  }
  </style>