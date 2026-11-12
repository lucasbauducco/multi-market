// Utilidades de formato compartidas.
const ars = new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 });
const ars2 = new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', minimumFractionDigits: 2 });

export function money(value, decimals = false) {
  const n = Number(value);
  if (Number.isNaN(n)) return '';
  return (decimals ? ars2 : ars).format(n);
}

export function finalPrice(product) {
  if (product.final_price !== undefined && product.final_price !== null) return Number(product.final_price);
  return Number(product.price) * (100 - Number(product.discount || 0)) / 100;
}

export function hasDiscount(product) {
  return Number(product.discount) > 0;
}

export function installment(price, n = 6) {
  return { n, amount: Number(price) / n };
}

export function dateTime(iso) {
  return new Date(iso).toLocaleString('es-AR', { dateStyle: 'short', timeStyle: 'short' });
}

export const ORDER_STATUS = {
  pending: { label: 'Pendiente', tone: 'warn' },
  confirmed: { label: 'Confirmado', tone: 'info' },
  delivered: { label: 'Entregado', tone: 'ok' },
  cancelled: { label: 'Cancelado', tone: 'bad' },
};

export const PAYMENT_STATUS = {
  unpaid: { label: 'Sin pagar', tone: 'warn' },
  pending: { label: 'Pago en revisión', tone: 'info' },
  paid: { label: 'Pagado', tone: 'ok' },
  failed: { label: 'Pago rechazado', tone: 'bad' },
  refunded: { label: 'Reembolsado', tone: 'neutral' },
};

export const PAYMENT_METHOD = {
  mercadopago: 'Mercado Pago',
  transfer: 'Transferencia',
  cash: 'Efectivo / retiro',
  link: 'Link de pago',
};

export const DELIVERY = { shipping: 'Envío a domicilio', pickup: 'Retiro en local' };

export function whatsappLink(phone, text) {
  const digits = String(phone || '').replace(/\D/g, '');
  if (!digits) return null;
  return `https://wa.me/${digits}${text ? `?text=${encodeURIComponent(text)}` : ''}`;
}
