<template>
  <section class="about-us">
    <h2 class="title-primary">Quiénes Somos</h2>
    <div class="content-wrapper">
      <div class="content">
        <img src="@/assets/image/product/jovenes-colegas-trabajando-juntos-cafeteria.jpg" alt="Nuestra Historia" class="side-image">
        <p class="title-text">Somos una empresa dedicada a ofrecer soluciones web a pequeños y medianos negocios que buscan expandir su presencia online, ofreciendo una páginas web para promocionar productos y servicios, además de integrar un sistema de ofertas y un mapa interactivo para localizar todos los negocios asociados.</p>
      </div>
      <div class="content">
        <p class="title-text">Estaremos trabajado con varias negocios de la region, ayudándolos a alcanzar sus objetivos de marketing digital y a aumentar su base de clientes de manera significativa.</p>
        <img src="@/assets/image/pc-celular.jpg" alt="Nuestro Equipo" class="side-image">
      </div>
      <div class="content">
        <img src="@/assets/image/blogpost.png" alt="Otro aspecto" class="side-image">
        <p class="title-text">Nuestro equipo se caracteriza por ser un grupo joven y dinámico, lleno de energía y con un firme deseo de superación y crecimiento. Compuesto por talentosos diseñadores web, desarrolladores innovadores y estrategas en marketing digital, todos compartimos la ambición de crecer profesionalmente mientras impulsamos el éxito de nuestros clientes.</p>

      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: "AboutUs",
};
</script>

<style scoped>
/* Estilos específicos del componente */
.about-us {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.content-wrapper {
  width: 100%;
}

.content {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-around;
  margin: 20px 0;
}

img.side-image {
  max-width: 400px;
  height: auto;
  flex: 1; /* Asegura que la imagen se ajuste correctamente dentro del contenedor */
}

p {
  max-width: 50%; /* Controla el ancho de los párrafos */
  text-align: justify;
  flex: 1; /* Permite que el texto ocupe el espacio restante */
  margin: 0 20px; /* Añade un poco de espacio alrededor del texto */
}

/* Ajustes responsivos */
@media (max-width: 768px) {
  .content {
    flex-direction: column;
  }

  img.side-image, p {
    max-width: 100%;
    flex: none;
  }
}
</style>
