<script setup>
import { RouterView } from 'vue-router'
import NavBar from '../components/NavBar.vue'
</script>

<template>
  <div class="app-layout">
    <NavBar />
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--color-bg);
}
.main-content {
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
  box-sizing: border-box;
}
</style>