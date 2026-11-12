<template>
    <div class="terms-container">
      <h1>Términos y Condiciones</h1>
      <p>Fecha de entrada en vigor: <strong>{{ currentDate }}</strong></p>
      <p>Bienvenido a <strong>Ciudad Oferta</strong>, la plataforma online que permite a negocios como el suyo exhibir y ofrecer sus productos a clientes potenciales. A continuación, se presentan los términos y condiciones que regulan el uso de nuestra página web y los servicios asociados. Al acceder y utilizar nuestra página, usted acepta estar sujeto por estos términos y condiciones, que aplican tanto a los negocios que listan productos como a los usuarios finales que navegan y realizan compras.</p>
      
      <h2>1. Servicios Ofrecidos</h2>
      <p><strong>Ciudad Oferta</strong> proporciona una plataforma en línea donde negocios pueden listar y publicitar sus productos. Nuestro servicio incluye la exhibición de productos, gestión de inventario y promoción a través de la plataforma. No participamos en el proceso de venta ni en las transacciones entre el negocio y el cliente. Toda transacción, comunicación y resolución de disputas son responsabilidad exclusiva del negocio y el cliente.</p>
  
      <h2>2. Responsabilidad de la Plataforma</h2>
      <p><strong>Ciudad Oferta</strong> no es parte ni se involucra en el acuerdo final entre compradores y vendedores. Cualquier contrato de venta es bilateral entre el comprador y el negocio.</p>
      <p>No garantizamos la calidad, seguridad, legalidad o disponibilidad de los productos ofrecidos en la plataforma por los negocios, ni la capacidad de los negocios para completar una venta o la capacidad de los compradores para completar una compra.</p>
  
      <!-- Continuar con los demás puntos de la misma manera -->
  
      <h2>9. Contacto</h2>
      <p>Si tiene preguntas o preocupaciones sobre estos términos y condiciones, por favor contacte a <strong>[información de contacto]</strong>.</p>
  
      <p>Al utilizar <strong>Ciudad Oferta</strong>, usted reconoce que ha leído, entendido y acordado estar sujeto por estos términos y condiciones.</p>
    </div>
  </template>
  
  <script>
  export default {
    name: 'TermsConditions',
  data() {
    return {
      currentDate: new Date().toLocaleDateString('es-ES')
    }
  }
  }
  </script>
  
  <style scoped>
  .terms-container {
    padding: 20px;
    margin: 1rem;
    background-color: #f4f4f4;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  }
  
  .terms-container h1, .terms-container h2 {
    color: #333;
  }
  
  .terms-container p {
    color: #666;
    line-height: 1.6;
  }
  
  .terms-container strong {
    color: #000;
  }
  </style>