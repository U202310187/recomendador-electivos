import { createApp } from 'vue'
import App from './App.vue'
import './assets/main.css'
import router from './router' // <-- 1. Importa el router

const app = createApp(App)

app.use(router) // <-- 2. Dile a Vue que use el router

app.mount('#app')