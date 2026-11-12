<template>
    <section class="carousel">
      <carousel  :autoplay="4000" :wrap-around="true">
        <slide v-for="(image, slide) in images" :key="slide" class="slide">
          <div class="carousel__item">
            <img :src="image" alt="Slide Image" style="width: 100vw;">
          </div>
        </slide>

        <template #addons>
          <Navigation />
          <Pagination />
        </template>
      </carousel>
      <router-view class="container-offers" name="offers" :shopId="-1" :isAuthenticate="false" ></router-view>
    </section>
    <section class="carousel">
      <carousel  :autoplay="4000" :wrap-around="true">
        <slide v-for="(image, slide) in images" :key="slide" class="slide">
          <div class="carousel__item">
            <img :src="image" alt="Slide Image" style="width: 100vw;">
          </div>
        </slide>

        <template #addons>
          <Navigation />
          <Pagination />
        </template>
      </carousel>
    </section>
  </template>
  
  <script>
  import 'vue3-carousel/dist/carousel.css'
  import { Carousel, Slide, Pagination, Navigation } from 'vue3-carousel'
  export default {
    name: 'HomeDjango',
    data() {
      return {
        images: [
          require('@/assets/image1.jpg'),
          require('@/assets/oferta-flashs-2semana-1536x400.jpg'),
          require('@/assets/image1.jpg'),
        ]
      }
    },
    components: {
      Carousel,
      Slide,
      Pagination,
      Navigation,
    }
    // Otras opciones del componente como data, methods, etc.
  };
  </script>
  
  <style>
  body{
    margin: 0;
    padding: 0;
  }
  </style>