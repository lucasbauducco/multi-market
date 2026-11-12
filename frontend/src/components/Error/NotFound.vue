<template>
  <div class="not-found">
    <h1>Página no encontrada</h1>
    <p>Lo sentimos, la página que buscas no existe.</p>
    <p>Estamos en constante crecimiento y construyendo la página junto a vos. Próximamente estará disponible.</p>
    <router-link to="/" class="back-home">Volver al inicio</router-link>
  </div>
</template>

<script>
export default {
  name: "NotFound",
};
</script>

<style>
.not-found {
  width: 100%;
  height: 100vh; /* Ajuste para que tome todo el viewport vertical */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  background-color: var(--color-5); /* Color de fondo para NotFound */
  color: var(--text); /* Color de texto general */
}

.title-primary {
  font-weight: 700;
  font-size: 2.5em; /* Ajusta según sea necesario */
  color: var(--color-2); /* Color específico para el título principal */
  margin-bottom: 0.5em;
}

.title-text {
  font-weight: 400;
  font-size: 1.5em; /* Ajusta según sea necesario */
  color: var(--text); /* Color de texto */
  line-height: 1.6;
  margin: 0.5em 0;
}

.back-home {
  font-weight: 500;
  font-size: 1em; /* Ajusta según sea necesario */
  color: var(--color-4); /* Color específico para el enlace de vuelta a inicio */
  text-decoration: none; /* Eliminar el subrayado de los enlaces */
  padding: 10px 20px;
  border: 2px solid var(--color-4); /* Borde del botón */
  border-radius: 5px; /* Bordes redondeados para el botón */
  transition: background-color 0.3s, color 0.3s; /* Transición suave para hover */
}

.back-home:hover {
  background-color: var(--color-4); /* Color de fondo al pasar el mouse */
  color: var(--color-5); /* Color de texto al pasar el mouse */
}
</style>
