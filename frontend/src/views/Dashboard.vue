<template>
  <div v-if="user">
    <div class="row mb-4">
      <div class="col">
        <h2>Dobrodošli, {{ user?.ime || '' }} {{ user?.prezime || '' }}!</h2>
      </div>
    </div>
    
    <div class="row">
      <!-- Kreiranje sobe - samo za profesore -->
      <div class="col-md-6 mb-4" v-if="isProfessor">
        <div class="card shadow h-100">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Kreiraj novu sobu</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleCreateRoom">
              <div class="mb-3">
                <label for="naziv" class="form-label">Naziv sobe</label>
                <input
                  type="text"
                  class="form-control"
                  id="naziv"
                  v-model="createForm.naziv"
                  required
                  placeholder="Unesite naziv sobe"
                >
              </div>
              
              <div class="mb-3">
                <label for="sifra" class="form-label">Šifra sobe</label>
                <input
                  type="text"
                  class="form-control"
                  id="sifra"
                  v-model="createForm.sifra"
                  required
                  placeholder="Unesite šifru sobe"
                >
                <div class="form-text">Ova šifra će se deliti sa drugim korisnicima</div>
              </div>
              
              <div class="mb-3">
                <label for="limit_sati" class="form-label">Vremensko ograničenje (sati)</label>
                <input
                  type="number"
                  class="form-control"
                  id="limit_sati"
                  v-model="createForm.limit_sati"
                  min="1"
                  max="168"
                  placeholder="Ostavite prazno za bez ograničenja"
                >
                <div class="form-text">Nakon ovog vremena soba će se automatski obrisati</div>
              </div>
              
              <div class="d-grid">
                <button type="submit" class="btn btn-primary" :disabled="createLoading">
                  <span v-if="createLoading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ createLoading ? 'Kreiranje...' : 'Kreiraj sobu' }}
                </button>
              </div>
            </form>
            
            <div v-if="createError" class="alert alert-danger mt-3">
              {{ createError }}
            </div>
            
            <div v-if="createSuccess" class="alert alert-success mt-3">
              {{ createSuccess }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Pridruživanje sobi -->
      <div class="col-md-6 mb-4" :class="{ 'col-md-12': !isProfessor }">
        <div class="card shadow h-100">
          <div class="card-header bg-success text-white">
            <h5 class="mb-0">Pridruži se sobi</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleJoinRoom">
              <div class="mb-3">
                <label for="join_sifra" class="form-label">Šifra sobe</label>
                <input
                  type="text"
                  class="form-control"
                  id="join_sifra"
                  v-model="joinForm.sifra"
                  required
                  placeholder="Unesite šifru sobe"
                >
              </div>
              
              <div class="d-grid">
                <button type="submit" class="btn btn-success" :disabled="joinLoading">
                  <span v-if="joinLoading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ joinLoading ? 'Pridruživanje...' : 'Pridruži se' }}
                </button>
              </div>
            </form>
            
            <div v-if="joinError" class="alert alert-danger mt-3">
              {{ joinError }}
            </div>
            
            <div v-if="joinSuccess" class="alert alert-success mt-3">
              {{ joinSuccess }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Moje sobe -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card shadow">
          <div class="card-header bg-warning text-dark">
            <h5 class="mb-0">Moje sobe</h5>
          </div>
          <div class="card-body">
            <div v-if="userRoomsLoading" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Učitavanje...</span>
              </div>
              <p class="mt-2">Učitavanje soba...</p>
            </div>
            
            <div v-else-if="userRooms.length === 0" class="text-center text-muted">
              <p>Niste učlanjeni u nijednu sobu.</p>
            </div>
            
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Naziv sobe</th>
                    <th>Šifra</th>
                    <th>Kreirao</th>
                    <th>Datum kreiranja</th>
                    <th>Akcije</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="room in userRooms" :key="room.id">
                    <td>{{ room.naziv }}</td>
                    <td><code>{{ room.sifra }}</code></td>
                    <td>{{ room.creator_name }}</td>
                    <td>{{ formatDate(room.created_at) }}</td>
                    <td>
                      <router-link :to="`/room/${room.id}`" class="btn btn-sm btn-primary">
                        <i class="bi bi-box-arrow-in-right"></i> Uđi u sobu
                      </router-link>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div v-if="userRoomsError" class="alert alert-danger mt-3">
              {{ userRoomsError }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Informacije o korisniku -->
    <div class="row">
      <div class="col-12">
        <div class="card shadow">
          <div class="card-header bg-info text-white">
            <h5 class="mb-0">Informacije o korisniku</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <p><strong>Ime:</strong> {{ user?.ime || 'N/A' }}</p>
                <p><strong>Prezime:</strong> {{ user?.prezime || 'N/A' }}</p>
                <p><strong>Email:</strong> {{ user?.email || 'N/A' }}</p>
              </div>
              <div class="col-md-6">
                <p><strong>Smer:</strong> {{ user?.smer || 'N/A' }}</p>
                <p><strong>Broj indeksa:</strong> {{ user?.broj_indeksa || 'N/A' }}</p>
                <p><strong>Rola:</strong> {{ user?.rola === 'student' ? 'Student' : 'Profesor' || 'N/A' }}</p>
              </div>
            </div>
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
import { ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { formatDate } from '../utils/dateUtils'

export default {
  name: 'Dashboard',
  setup() {
    const store = useStore()
    const router = useRouter()
    const { user, isProfessor } = useAuth()
    
    // Sobe korisnika
    const userRooms = ref([])
    const userRoomsLoading = ref(false)
    const userRoomsError = ref('')
    
    const createForm = reactive({
      naziv: '',
      sifra: '',
      limit_sati: ''
    })
    
    const joinForm = reactive({
      sifra: ''
    })
    
    const createLoading = ref(false)
    const createError = ref('')
    const createSuccess = ref('')
    
    const joinLoading = ref(false)
    const joinError = ref('')
    const joinSuccess = ref('')
    
    const handleCreateRoom = async () => {
      createLoading.value = true
      createError.value = ''
      createSuccess.value = ''
      
      const result = await store.dispatch('createRoom', createForm)
      
      if (result.success) {
        createSuccess.value = `Soba uspešno kreirana!`
        createForm.naziv = ''
        createForm.sifra = ''
        createForm.limit_sati = ''
        
        // Osvežavanje liste soba
        loadUserRooms()
        
        // Automatski prelazak u sobu
        setTimeout(() => {
          router.push(`/room/${result.roomId}`)
        }, 2000)
      } else {
        createError.value = result.error
      }
      
      createLoading.value = false
    }
    
    const handleJoinRoom = async () => {
      joinLoading.value = true
      joinError.value = ''
      joinSuccess.value = ''
      
      const result = await store.dispatch('joinRoom', joinForm.sifra)
      
      if (result.success) {
        joinSuccess.value = `Uspešno pridruživanje sobi: ${result.roomName}`
        joinForm.sifra = ''
        
        // Osvežavanje liste soba
        loadUserRooms()
        
        // Automatski prelazak u sobu
        setTimeout(() => {
          router.push(`/room/${result.roomId}`)
        }, 2000)
      } else {
        joinError.value = result.error
      }
      
      joinLoading.value = false
    }
    
    const loadUserRooms = async () => {
      userRoomsLoading.value = true
      userRoomsError.value = ''
      
      console.log('Loading user rooms...')
      const result = await store.dispatch('getUserRooms')
      console.log('User rooms result:', result)
      
      if (result.success) {
        userRooms.value = result.rooms
        console.log('User rooms loaded:', userRooms.value)
      } else {
        userRoomsError.value = result.error
        console.error('Error loading user rooms:', result.error)
      }
      
      userRoomsLoading.value = false
    }
    
    // formatDate je importovan iz utils/dateUtils.js
    
    // Učitavanje soba pri mount-u
    onMounted(() => {
      loadUserRooms()
    })
    
    return {
      user,
      isProfessor,
      userRooms,
      userRoomsLoading,
      userRoomsError,
      createForm,
      joinForm,
      createLoading,
      createError,
      createSuccess,
      joinLoading,
      joinError,
      joinSuccess,
      handleCreateRoom,
      handleJoinRoom,
      formatDate
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
