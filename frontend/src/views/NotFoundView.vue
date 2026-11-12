<template>
  <div class="container page">
    <empty-state icon="🧭" title="Página no encontrada" text="La página que buscás no existe o fue movida." to="/" cta="Ir al inicio" />
  </div>
</template>

<script>
import EmptyState from '@/components/ui/EmptyState.vue';

export default { name: 'NotFoundView', components: { EmptyState }, mounted() { document.title = 'No encontrado – Multi-Market'; } };
</script>
