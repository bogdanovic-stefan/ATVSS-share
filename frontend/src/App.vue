<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary" v-if="isAuthenticated">
      <div class="container">
        <router-link class="navbar-brand" to="/dashboard">ATVSS share</router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/dashboard">Početna</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/profile">Profil</router-link>
            </li>
          </ul>
          <ul class="navbar-nav">
            <li class="nav-item">
              <a class="nav-link" href="#" @click="logout" title="Odjava">
                <i class="bi bi-box-arrow-right"></i>
              </a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    
    <div class="container mt-4">
      <router-view />
    </div>
    
    <Footer />
  </div>
</template>

<script>
import Footer from './components/Footer.vue'
import { useAuth } from './composables/useAuth'

export default {
  name: 'App',
  components: {
    Footer
  },
  setup() {
    const { isAuthenticated, logout } = useAuth()
    
    return {
      isAuthenticated,
      logout
    }
  }
}
</script>

<style>
#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar-brand {
  font-weight: bold;
}

.container {
  max-width: 1200px;
}

/* Glavni sadržaj zauzima sav dostupan prostor */
.container.mt-4 {
  flex: 1;
  margin-bottom: 3rem; /* Dodajemo margin na dno sadržaja */
}

/* Footer ide na dnu */
.footer {
  background-color: #343a40 !important;
  border-top: 1px solid #495057;
  margin-top: auto;
}
</style>
