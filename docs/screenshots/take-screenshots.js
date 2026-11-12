const { chromium } = require('playwright-core');
const out = process.argv[2] || 'C:/Users/Lucas/orca/multi-market/docs/screenshots';
const B = 'http://localhost:8081';
const API = 'http://127.0.0.1:8010';

(async () => {
  const browser = await chromium.launch({ executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1360, height: 860 }, locale: 'es-AR', deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push('PAGEERROR ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('CONSOLE ' + m.text().slice(0, 160)); });
  const settle = async () => { await page.waitForLoadState('networkidle'); await page.waitForTimeout(900); };
  const shot = async (name, full = false) => {
    await settle();
    await page.screenshot({ path: `${out}/${name}.png`, fullPage: full });
    console.log('shot', name, page.url().replace(B, ''));
  };
  const go = async (path) => { await page.goto(B + path, { waitUntil: 'networkidle' }); };

  // ids reales
  const home = await (await fetch(API + '/api/home/')).json();
  const catTech = home.categories.find(c => c.name === 'Tecnología');
  const find = async (q) => (await (await fetch(`${API}/api/search_products/?query=${encodeURIComponent(q)}`)).json()).products[0];
  const phone = await find('Smartphone Aurora');
  const sofa = await find('Sofá de terciopelo');
  const coffee = await find('Café en grano');

  await go('/');
  await shot('01-home');
  { const h = await page.evaluate(() => document.body.scrollHeight);
    for (let y = 0; y < h; y += 500) { await page.evaluate(v => window.scrollTo(0, v), y); await page.waitForTimeout(120); }
    await page.evaluate(() => window.scrollTo(0, 0)); }
  await shot('01b-home-completa', true);
  await go('/buscar?discounted=1&ordering=discount');
  await shot('02-ofertas');
  await go(`/buscar?category=${catTech.id}`);
  await shot('03-categoria');
  await go(`/producto/${phone.id}`);
  await shot('04-producto');
  await go(`/producto/${sofa.id}`);
  await shot('04b-producto-galeria');

  // carrito lateral
  await go(`/producto/${phone.id}`);
  await page.locator('.buy').getByRole('button', { name: 'Agregar al carrito' }).click();
  await go(`/producto/${coffee.id}`);
  await page.locator('.buy').getByRole('button', { name: 'Agregar al carrito' }).click();
  await page.waitForSelector('.drawer');
  await shot('05-carrito-lateral');
  await page.getByRole('button', { name: 'Finalizar compra' }).click();

  // checkout
  await page.waitForURL('**/checkout');
  await page.getByLabel('Nombre y apellido').fill('Ana Pérez');
  await page.getByLabel('Teléfono / WhatsApp').fill('+54 9 11 5555 0000');
  await page.getByLabel('Email').fill('ana@example.com');
  await shot('06-checkout-datos');
  await page.getByRole('button', { name: 'Continuar' }).first().click();
  await page.getByText('Retiro en el local').first().click();
  await page.locator('form:visible').getByRole('button', { name: 'Continuar' }).click();
  await shot('07-checkout-pago');
  // un pedido por transferencia, otro efectivo
  await page.locator('input[value="transfer"]').first().check();
  await page.getByRole('button', { name: 'Continuar' }).last().click();
  await shot('08-checkout-confirmar');
  await page.getByRole('button', { name: /Confirmar pedido/ }).click();
  await page.waitForSelector('.ok-head');
  await shot('09-pedido-creado');
  await page.getByRole('link', { name: /Ver instrucciones de pago/ }).first().click();
  await page.waitForSelector('.timeline');
  await shot('10-seguimiento-pedido');

  await go('/tienda/casa-bella');
  await shot('11-tienda');
  await go('/registro');
  await shot('12-registro-tienda');

  // panel
  await go('/ingresar');
  await page.getByLabel('Usuario').fill('techzone');
  await page.getByLabel('Contraseña').fill('demo12345');
  await page.getByRole('button', { name: 'Ingresar' }).click();
  await page.waitForURL('**/panel');
  await shot('13-panel-resumen');
  await go('/panel/productos');
  await shot('14-panel-productos');
  await go('/panel/pedidos');
  await shot('15-panel-pedidos');
  await go('/panel/configuracion');
  await shot('16-panel-cobros', true);

  // mobile
  const m = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, locale: 'es-AR' });
  const mp = await m.newPage();
  await mp.goto(B + '/', { waitUntil: 'networkidle' }); await mp.waitForTimeout(900);
  await mp.screenshot({ path: `${out}/17-movil-home.png` });
  await mp.goto(`${B}/producto/${phone.id}`, { waitUntil: 'networkidle' }); await mp.waitForTimeout(900);
  await mp.screenshot({ path: `${out}/18-movil-producto.png` });
  console.log('shot mobile');
  console.log(errors.length ? errors.join('\n') : 'NO CONSOLE ERRORS');
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
