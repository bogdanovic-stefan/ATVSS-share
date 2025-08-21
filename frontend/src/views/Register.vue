<template>
  <div class="row justify-content-center">
    <div class="col-md-8 col-lg-6">
      <div class="card shadow">
        <div class="card-header bg-success text-white text-center">
          <h4 class="mb-0">Registracija Studenta</h4>
        </div>
        <div class="card-body">
          <form @submit.prevent="handleRegister">
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="ime" class="form-label">Ime</label>
                <input
                  type="text"
                  class="form-control"
                  id="ime"
                  v-model="form.ime"
                  required
                  placeholder="Unesite ime"
                >
              </div>
              
              <div class="col-md-6 mb-3">
                <label for="prezime" class="form-label">Prezime</label>
                <input
                  type="text"
                  class="form-control"
                  id="prezime"
                  v-model="form.prezime"
                  required
                  placeholder="Unesite prezime"
                >
              </div>
            </div>
            
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
            
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="smer" class="form-label">Smer</label>
                <select class="form-select" id="smer" v-model="form.smer" required>
                  <option value="">Izaberite smer</option>
                  <option value="SRT">SRT</option>
                  <option value="KOT">KOT</option>
                </select>
              </div>
              
              <div class="col-md-6 mb-3">
                <label for="broj_indeksa" class="form-label">Broj indeksa</label>
                <input
                  type="text"
                  class="form-control"
                  id="broj_indeksa"
                  v-model="form.broj_indeksa"
                  required
                  placeholder="Unesite broj indeksa"
                >
              </div>
            </div>
            
            <div class="mb-3">
              <label for="lozinka" class="form-label">Lozinka</label>
              <input
                type="password"
                class="form-control"
                id="lozinka"
                v-model="form.lozinka"
                required
                placeholder="Unesite lozinku"
                minlength="6"
              >
            </div>
            
            <div class="mb-3">
              <label for="potvrda_lozinke" class="form-label">Potvrda lozinke</label>
              <input
                type="password"
                class="form-control"
                id="potvrda_lozinke"
                v-model="potvrdaLozinke"
                required
                placeholder="Potvrdite lozinku"
              >
              <div v-if="lozinkeSeNePoklapaju" class="text-danger small mt-1">
                Lozinke se ne poklapaju
              </div>
            </div>
            
            <div class="d-grid">
              <button type="submit" class="btn btn-success" :disabled="loading || lozinkeSeNePoklapaju">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ loading ? 'Registracija...' : 'Registruj se' }}
              </button>
            </div>
          </form>
          
          <div v-if="error" class="alert alert-danger mt-3">
            {{ error }}
          </div>
          
          <div v-if="success" class="alert alert-success mt-3">
            {{ success }}
          </div>
          
          <hr class="my-4">
          
          <div class="text-center">
            <p class="mb-0">Već imate nalog?</p>
            <router-link to="/login" class="btn btn-outline-success">
              Prijavite se
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'Register',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const form = reactive({
      ime: '',
      prezime: '',
      email: '',
      smer: '',
      broj_indeksa: '',
      lozinka: ''
    })
    
    const potvrdaLozinke = ref('')
    const loading = ref(false)
    const error = ref('')
    const success = ref('')
    
    const lozinkeSeNePoklapaju = computed(() => {
      return form.lozinka && potvrdaLozinke.value && form.lozinka !== potvrdaLozinke.value
    })
    
    const handleRegister = async () => {
      if (lozinkeSeNePoklapaju.value) {
        error.value = 'Lozinke se ne poklapaju'
        return
      }
      
      loading.value = true
      error.value = ''
      success.value = ''
      
      const result = await store.dispatch('register', form)
      
      if (result.success) {
        success.value = 'Uspešna registracija! Možete se prijaviti.'
        form.ime = ''
        form.prezime = ''
        form.email = ''
        form.smer = ''
        form.broj_indeksa = ''
        form.lozinka = ''
        potvrdaLozinke.value = ''
      } else {
        error.value = result.error
      }
      
      loading.value = false
    }
    
    return {
      form,
      potvrdaLozinke,
      loading,
      error,
      success,
      lozinkeSeNePoklapaju,
      handleRegister
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




















