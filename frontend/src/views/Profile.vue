<template>
  <div v-if="user" class="row justify-content-center">
    <div class="col-md-8 col-lg-6">
      <div class="card shadow">
        <div class="card-header bg-info text-white text-center">
          <h4 class="mb-0">Moj Profil</h4>
        </div>
        <div class="card-body">
          <!-- Prikaz podataka (read-only) -->
          <div v-if="!isEditing">
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label fw-bold">Ime</label>
                <p class="form-control-plaintext">{{ user?.ime || 'N/A' }}</p>
              </div>
              
              <div class="col-md-6 mb-3">
                <label class="form-label fw-bold">Prezime</label>
                <p class="form-control-plaintext">{{ user?.prezime || 'N/A' }}</p>
              </div>
            </div>
            
            <div class="mb-3">
              <label class="form-label fw-bold">Email</label>
              <p class="form-control-plaintext">{{ user?.email || 'N/A' }}</p>
              <div class="form-text">Email se ne može menjati</div>
            </div>
            
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label fw-bold">Smer</label>
                <p class="form-control-plaintext">{{ user?.smer || 'N/A' }}</p>
              </div>
              
              <div class="col-md-6 mb-3">
                <label class="form-label fw-bold">Broj indeksa</label>
                <p class="form-control-plaintext">{{ user?.broj_indeksa || 'N/A' }}</p>
              </div>
            </div>
            
            <div class="mb-3">
              <label class="form-label fw-bold">Rola</label>
              <p class="form-control-plaintext">{{ user?.rola === 'student' ? 'Student' : 'Profesor' }}</p>
              <div class="form-text">Rola se ne može menjati</div>
            </div>
            
            <div class="d-grid">
              <button @click="startEditing" class="btn btn-info">
                <i class="bi bi-pencil"></i> Izmeni profil
              </button>
            </div>
          </div>
          
          <!-- Forma za editovanje -->
          <form v-else @submit.prevent="handleUpdateProfile">
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
                :value="user?.email || ''"
                disabled
                placeholder="Email"
              >
              <div class="form-text">Email se ne može menjati</div>
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
              <label for="rola" class="form-label">Rola</label>
              <input
                type="text"
                class="form-control"
                id="rola"
                :value="user?.rola === 'student' ? 'Student' : 'Profesor'"
                disabled
                placeholder="Rola"
              >
              <div class="form-text">Rola se ne može menjati</div>
            </div>
            
            <div class="d-grid gap-2">
              <button type="submit" class="btn btn-success" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ loading ? 'Ažuriranje...' : 'Sačuvaj izmene' }}
              </button>
              <button type="button" @click="cancelEditing" class="btn btn-outline-secondary">
                Otkaži
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
            <router-link to="/dashboard" class="btn btn-outline-secondary">
              Nazad na početnu
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="text-center mt-5">
    <div class="spinner-border" role="status">
      <span class="visually-hidden">Učitavanje...</span>
    </div>
    <p class="mt-3">Učitavanje podataka...</p>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'Profile',
  setup() {
    const store = useStore()
    
    const user = computed(() => store.getters.user)
    
    const form = reactive({
      ime: '',
      prezime: '',
      smer: '',
      broj_indeksa: ''
    })
    
    const loading = ref(false)
    const error = ref('')
    const success = ref('')
    const isEditing = ref(false)
    
    const loadUserData = () => {
      if (user.value) {
        form.ime = user.value.ime || ''
        form.prezime = user.value.prezime || ''
        form.smer = user.value.smer || ''
        form.broj_indeksa = user.value.broj_indeksa || ''
      }
    }
    
    const startEditing = () => {
      loadUserData() // Ucitaj trenutne podatke u formu
      isEditing.value = true
      error.value = ''
      success.value = ''
    }
    
    const cancelEditing = () => {
      isEditing.value = false
      error.value = ''
      success.value = ''
    }
    
    const handleUpdateProfile = async () => {
      loading.value = true
      error.value = ''
      success.value = ''
      
      const result = await store.dispatch('updateProfile', form)
      
      if (result.success) {
        success.value = 'Profil uspešno ažuriran'
        isEditing.value = false // Vrati na prikaz podataka
      } else {
        error.value = result.error
      }
      
      loading.value = false
    }
    
    onMounted(() => {
      loadUserData()
    })
    
    return {
      user,
      form,
      loading,
      error,
      success,
      isEditing,
      startEditing,
      cancelEditing,
      handleUpdateProfile
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

.form-control:disabled {
  background-color: #f8f9fa;
  opacity: 0.7;
}

.form-control-plaintext {
  padding: 0.375rem 0.75rem;
  margin-bottom: 0;
  color: #212529;
  background-color: transparent;
  border: solid transparent;
  border-width: 1px 0;
  font-size: 1rem;
  line-height: 1.5;
  border-radius: 0.375rem;
}

.form-control-plaintext:hover {
  background-color: #f8f9fa;
  border-radius: 0.375rem;
}

.form-label.fw-bold {
  color: #495057;
  font-weight: 600;
}
</style>
