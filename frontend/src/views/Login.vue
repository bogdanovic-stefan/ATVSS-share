<template>
  <div class="row justify-content-center">
    <div class="col-md-6 col-lg-4">
      <div class="card shadow">
        <div class="card-header bg-primary text-white text-center">
          <h4 class="mb-0">Prijava</h4>
        </div>
        <div class="card-body">
          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label for="email" class="form-label">Email</label>
              <input
                type="email"
                class="form-control"
                id="email"
                v-model="form.email"
                required
                placeholder="Unesite email"
              >
            </div>
            
            <div class="mb-3">
              <label for="password" class="form-label">Lozinka</label>
              <input
                type="password"
                class="form-control"
                id="password"
                v-model="form.lozinka"
                required
                placeholder="Unesite lozinku"
              >
            </div>
            
            <div class="d-grid">
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ loading ? 'Prijavljivanje...' : 'Prijavi se' }}
              </button>
            </div>
          </form>
          
          <div v-if="error" class="alert alert-danger mt-3">
            {{ error }}
          </div>
          
          <hr class="my-4">
          
          <div class="text-center">
            <p class="mb-0">Nemate nalog?</p>
            <router-link to="/register" class="btn btn-outline-primary">
              Registrujte se
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const form = reactive({
      email: '',
      lozinka: ''
    })
    
    const loading = ref(false)
    const error = ref('')
    
    const handleLogin = async () => {
      loading.value = true
      error.value = ''
      
      const result = await store.dispatch('login', form)
      
      if (result.success) {
        router.push('/dashboard')
      } else {
        error.value = result.error
      }
      
      loading.value = false
    }
    
    return {
      form,
      loading,
      error,
      handleLogin
    }
  }
}
</script>

<style scoped>
.card {
  border: none;
  border-radius: 15px;
}

.card-header {
  border-radius: 15px 15px 0 0 !important;
}

.btn {
  border-radius: 8px;
}
</style>




















