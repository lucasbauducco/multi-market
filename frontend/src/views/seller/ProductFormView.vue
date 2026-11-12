<template>
  <div class="stack">
    <div class="row"><router-link to="/panel/productos" class="btn btn-ghost btn-sm">← Volver</router-link><h1>{{ isEdit ? 'Editar producto' : 'Nuevo producto' }}</h1></div>

    <form class="layout" @submit.prevent="save">
      <section class="card card-pad">
        <div class="field"><label for="nm">Nombre</label><input id="nm" v-model.trim="f.name" class="input" required maxlength="200" /></div>
        <div class="field"><label for="ds">Descripción</label><textarea id="ds" v-model.trim="f.description" class="input" required rows="5"></textarea></div>
        <div class="grid-2">
          <div class="field"><label for="pr">Precio ($)</label><input id="pr" v-model="f.price" type="number" min="0" step="0.01" class="input" required /></div>
          <div class="field"><label for="dc">Descuento (%)</label><input id="dc" v-model="f.discount" type="number" min="0" max="100" step="1" class="input" /></div>
        </div>
        <div class="grid-2">
          <div class="field"><label for="st">Stock</label><input id="st" v-model="f.stock" type="number" min="0" class="input" placeholder="Vacío = sin control" /><span class="hint">Dejalo vacío si no querés controlar stock.</span></div>
          <div class="field"><label for="bc">Código / SKU</label><input id="bc" v-model.trim="f.barcode" class="input" maxlength="100" placeholder="Se genera solo si lo dejás vacío" /></div>
        </div>
        <div class="grid-2">
          <div class="field"><label for="sc">Categoría</label>
            <select id="sc" v-model="f.subcategory" class="input"><option :value="null">Sin categoría</option>
              <optgroup v-for="c in groups" :key="c.name" :label="c.name"><option v-for="s in c.subs" :key="s.id" :value="s.id">{{ s.name }}</option></optgroup>
            </select>
          </div>
          <div class="field"><label for="se">Estado</label><select id="se" v-model="f.state" class="input"><option value="active">Activo (visible)</option><option value="inactive">Pausado (oculto)</option></select></div>
        </div>
        <p v-if="error" class="alert alert-bad">{{ error }}</p>
        <div class="row"><button class="btn btn-lg" :disabled="busy">{{ busy ? 'Guardando…' : 'Guardar producto' }}</button><router-link to="/panel/productos" class="btn btn-ghost btn-lg">Cancelar</router-link></div>
      </section>

      <aside class="card card-pad">
        <h2>Imágenes</h2>
        <div class="drop" :class="{ over }" @dragover.prevent="over = true" @dragleave="over = false" @drop.prevent="onDrop">
          <p>Arrastrá fotos acá o</p>
          <label class="btn btn-soft btn-sm">Elegir archivos<input type="file" accept="image/*" multiple class="visually-hidden" @change="onPick" /></label>
          <p class="hint">PNG, JPG o WEBP · hasta 3 MB c/u · máx. 8</p>
        </div>
        <div v-if="existing.length" class="label mt">Actuales</div>
        <div class="thumbs"><div v-for="(u, i) in existing" :key="u" class="th"><img :src="u" alt="" /><span v-if="i === 0" class="badge badge-ok">Principal</span></div></div>
        <div v-if="added.length" class="label mt">Nuevas</div>
        <div class="thumbs">
          <div v-for="(a, i) in added" :key="i" class="th"><img :src="a" alt="" />
            <button type="button" class="x" aria-label="Quitar" @click="added.splice(i, 1)">✕</button>
            <span v-if="!isEdit && i === 0" class="badge badge-ok">Principal</span></div>
        </div>
        <p v-if="isEdit" class="hint">Las imágenes nuevas se agregan a la galería. Si no había imagen principal, la primera nueva lo será.</p>
      </aside>
    </form>
  </div>
</template>

<script>
import api, { errorMessage } from '@/api';

export default {
  name: 'ProductFormView',
  data() {
    return {
      f: { name: '', description: '', price: '', discount: 0, stock: '', barcode: '', subcategory: null, state: 'active' },
      groups: [], existing: [], added: [], over: false, busy: false, error: '',
    };
  },
  computed: {
    isEdit() { return !!this.$route.params.id; },
  },
  methods: {
    readFiles(files) {
      Array.from(files).slice(0, 8).forEach((file) => {
        if (!file.type.startsWith('image/')) return;
        const r = new FileReader();
        r.onload = () => { if (this.added.length + this.existing.length < 8) this.added.push(r.result); };
        r.readAsDataURL(file);
      });
    },
    onPick(e) { this.readFiles(e.target.files); e.target.value = ''; },
    onDrop(e) { this.over = false; this.readFiles(e.dataTransfer.files); },
    async save() {
      this.busy = true; this.error = '';
      const body = {
        name: this.f.name, description: this.f.description, price: this.f.price,
        discount: this.f.discount === '' ? 0 : this.f.discount,
        stock: this.f.stock === '' || this.f.stock === null ? null : Number(this.f.stock),
        barcode: this.f.barcode || `MM-${Date.now().toString(36).toUpperCase()}`,
        subcategory: this.f.subcategory, state: this.f.state,
      };
      if (this.added.length) {
        if (!this.existing.length) { body.image_base64 = this.added[0]; body.images_base64 = this.added.slice(1); } else { body.images_base64 = this.added; }
      }
      try {
        if (this.isEdit) await api.patch(`/api/products/${this.$route.params.id}/`, body);
        else await api.post('/api/products/', body);
        this.$router.push('/panel/productos');
      } catch (e) { this.error = errorMessage(e, 'No pudimos guardar el producto.'); } finally { this.busy = false; }
    },
  },
  async mounted() {
    document.title = 'Producto – Multi-Market';
    try {
      const subs = (await api.get('/api/subcategories/')).data;
      const cats = (await api.get('/api/categories/')).data;
      const byCat = {};
      cats.forEach((c) => { byCat[c.id] = { name: c.name, subs: [] }; });
      subs.forEach((s) => { (s.category && byCat[s.category] ? byCat[s.category] : (byCat.other = byCat.other || { name: 'Otras', subs: [] })).subs.push(s); });
      this.groups = Object.values(byCat).filter(g => g.subs.length);
      if (this.isEdit) {
        const p = (await api.get(`/api/products/${this.$route.params.id}/`)).data;
        this.f = { name: p.name, description: p.description, price: p.price, discount: Number(p.discount), stock: p.stock === null ? '' : p.stock, barcode: p.barcode, subcategory: p.subcategory, state: p.state };
        this.existing = p.images || [];
      }
    } catch (e) { this.error = errorMessage(e, 'No pudimos cargar los datos.'); }
  },
};
</script>

<style scoped>
.layout { display: grid; grid-template-columns: 1.4fr 1fr; gap: 16px; align-items: start; }
.drop { border: 2px dashed #cfd3e2; border-radius: 14px; padding: 18px; text-align: center; background: #fafbff; }
.drop.over { border-color: var(--brand-500); background: var(--brand-50); }
.drop p { margin: 0 0 8px; }
.mt { margin-top: 14px; }
.thumbs { display: grid; grid-template-columns: repeat(auto-fill, minmax(86px, 1fr)); gap: 8px; margin-top: 8px; }
.th { position: relative; aspect-ratio: 1; border-radius: 10px; overflow: hidden; background: #eef0f7; }
.th img { width: 100%; height: 100%; object-fit: cover; }
.th .badge { position: absolute; left: 4px; bottom: 4px; }
.x { position: absolute; top: 4px; right: 4px; width: 22px; height: 22px; border-radius: 50%; border: 0; background: rgba(0, 0, 0, .6); color: #fff; cursor: pointer; }
@media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }
</style>
