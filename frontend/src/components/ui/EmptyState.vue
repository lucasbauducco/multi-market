<template>
  <div class="empty card card-pad">
    <div class="ico" aria-hidden="true">{{ icon }}</div>
    <h3>{{ title }}</h3>
    <p class="muted"><slot>{{ text }}</slot></p>
    <router-link v-if="to" :to="to" class="btn">{{ cta }}</router-link>
  </div>
</template>

<script>
export default { name: 'EmptyState', props: { icon: { type: String, default: '🛍️' }, title: String, text: String, to: [String, Object], cta: String } };
</script>

<style scoped>
.empty { text-align: center; padding: 42px 18px; }
.ico { font-size: 2.6rem; margin-bottom: 6px; }
</style>
