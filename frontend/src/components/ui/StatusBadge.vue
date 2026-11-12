<template><span class="badge" :class="`badge-${info.tone}`">{{ info.label }}</span></template>

<script>
import { ORDER_STATUS, PAYMENT_STATUS } from '@/utils';

export default {
  name: 'StatusBadge',
  props: { kind: { type: String, default: 'order' }, value: String },
  computed: {
    info() {
      const map = this.kind === 'payment' ? PAYMENT_STATUS : ORDER_STATUS;
      return map[this.value] || { label: this.value, tone: 'neutral' };
    },
  },
};
</script>
