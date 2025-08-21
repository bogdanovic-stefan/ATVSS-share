<template>
  <div v-if="user">
    <div class="row mb-4">
      <div class="col">
                  <div class="d-flex justify-content-between align-items-center">
                        <div>
              <h2>{{ roomInfo?.naziv || `Soba #${roomId}` }}</h2>
              <p v-if="roomInfo?.sifra" class="text-muted">
                <small>Šifra sobe: <span class="text-primary">{{ roomInfo.sifra }}</span></small>
              </p>
            </div>
            <div class="d-flex gap-2">
              <button 
                v-if="isRoomCreator" 
                @click="deleteRoom" 
                class="btn btn-danger"
                title="Obriši sobu (samo kreator može)"
              >
                <i class="bi bi-trash3"></i> Obriši sobu
              </button>
              <button @click="leaveRoom" class="btn btn-outline-danger">
                <i class="bi bi-door-open"></i> Napusti sobu
              </button>
            </div>
        </div>
      </div>
    </div>
    
    <!-- Upload fajla -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Upload fajla <small class="text-light">(max 100 MB)</small></h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleUpload">
              <div class="row">
                <div class="col-md-8">
                  <input
                    type="file"
                    class="form-control"
                    ref="fileInput"
                    @change="handleFileSelect"
                    required
                  >
                </div>
                <div class="col-md-4">
                  <button type="submit" class="btn btn-primary w-100" :disabled="uploadLoading">
                    <span v-if="uploadLoading" class="spinner-border spinner-border-sm me-2"></span>
                    {{ uploadLoading ? 'Upload...' : 'Upload fajl' }}
                  </button>
                </div>
              </div>
            </form>
            
            <div v-if="uploadError" class="alert alert-danger mt-3">
              {{ uploadError }}
            </div>
            
            <div v-if="uploadSuccess" class="alert alert-success mt-3">
              {{ uploadSuccess }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Lista fajlova -->
    <div class="row">
      <div class="col-12">
        <div class="card shadow">
          <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Fajlovi u sobi</h5>
            <button @click="refreshFiles" class="btn btn-light btn-sm">
              <i class="bi bi-arrow-clockwise"></i> Osveži
            </button>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Učitavanje...</span>
              </div>
            </div>
            
            <div v-else-if="files.length === 0" class="text-center py-4">
              <p class="text-muted">Nema fajlova u ovoj sobi</p>
            </div>
            
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Naziv fajla</th>
                    <th>Postavio</th>
                    <th>Datum</th>
                    <th>Akcije</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="file in files" :key="file.id">
                    <td>{{ file.original_filename }}</td>
                    <td>{{ file.ime }} {{ file.prezime }}</td>
                    <td>{{ formatDate(file.upload_time) }}</td>
                    <td>
                      <div class="btn-group" role="group">
                        <button 
                          @click="downloadFile(file.id)" 
                          class="btn btn-sm btn-outline-primary"
                          title="Preuzmi fajl"
                        >
                          <i class="bi bi-cloud-download"></i>
                        </button>
                        <button 
                          v-if="canDeleteFile(file)"
                          @click="deleteFile(file.id)" 
                          class="btn btn-sm btn-outline-danger"
                          :title="user?.rola === 'profesor' ? 'Obriši fajl (profesor)' : 'Obriši svoj fajl'"
                        >
                          <i class="bi bi-trash3"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div v-if="filesError" class="alert alert-danger mt-3">
              {{ filesError }}
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
import { ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { formatDate } from '../utils/dateUtils'
import axios from 'axios'

export default {
  name: 'Room',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    const { user } = useAuth()
    
    const roomId = route.params.id
    
    const roomInfo = ref(null)
    const roomLoading = ref(false)
    const roomError = ref('')
    
    const files = ref([])
    const loading = ref(false)
    const filesError = ref('')
    
    // Computed property za proveru da li je korisnik kreator sobe
    const isRoomCreator = computed(() => {
      return roomInfo.value && user.value && roomInfo.value.creator_id === user.value.id
    })
    
    const uploadLoading = ref(false)
    const uploadError = ref('')
    const uploadSuccess = ref('')
    const selectedFile = ref(null)
    
    const fileInput = ref(null)
    
    const loadRoomInfo = async () => {
      roomLoading.value = true
      roomError.value = ''
      
      const result = await store.dispatch('getRoomInfo', roomId)
      
      if (result.success) {
        roomInfo.value = result.room
      } else {
        roomError.value = result.error
      }
      
      roomLoading.value = false
    }
    
    const loadFiles = async () => {
      loading.value = true
      filesError.value = ''
      
      const result = await store.dispatch('getRoomFiles', roomId)
      
      if (result.success) {
        files.value = result.files
      } else {
        filesError.value = result.error
      }
      
      loading.value = false
    }
    
    const refreshFiles = () => {
      loadFiles()
    }
    
    const handleFileSelect = (event) => {
      selectedFile.value = event.target.files[0]
    }
    
    const handleUpload = async () => {
      if (!selectedFile.value) {
        uploadError.value = 'Molimo izaberite fajl'
        return
      }
      
      uploadLoading.value = true
      uploadError.value = ''
      uploadSuccess.value = ''
      
      const result = await store.dispatch('uploadFile', {
        roomId: parseInt(roomId),
        file: selectedFile.value
      })
      
      if (result.success) {
        uploadSuccess.value = 'Fajl uspešno uploadovan'
        selectedFile.value = null
        if (fileInput.value) {
          fileInput.value.value = ''
        }
        loadFiles() // Osvežavanje liste fajlova
      } else {
        uploadError.value = result.error
      }
      
      uploadLoading.value = false
    }
    
    const downloadFile = async (fileId) => {
      const result = await store.dispatch('downloadFile', fileId)
      if (!result.success) {
        alert(result.error || 'Greška pri preuzimanju fajla')
      }
    }
    
    const deleteFile = async (fileId) => {
      if (!confirm('Da li ste sigurni da želite da obrišete ovaj fajl?')) {
        return
      }
      
      const result = await store.dispatch('deleteFile', fileId)
      
      if (result.success) {
        loadFiles() // Osvežavanje liste fajlova
      } else {
        alert(result.error)
      }
    }
    
    const deleteRoom = async () => {
      if (!confirm('Da li ste sigurni da želite da obrišete ovu sobu? Ova akcija se ne može poništiti i svi fajlovi će biti obrisani.')) {
        return
      }
      
      const result = await store.dispatch('deleteRoom', parseInt(roomId))
      
      if (result.success) {
        alert('Soba uspešno obrisana')
        router.push('/dashboard')
      } else {
        alert(result.error)
      }
    }
    
    const leaveRoom = async () => {
      if (!confirm('Da li ste sigurni da želite da napustite ovu sobu?')) {
        return
      }
      
      const result = await store.dispatch('leaveRoom', parseInt(roomId))
      
      if (result.success) {
        router.push('/dashboard')
      } else {
        alert(result.error)
      }
    }
    
    const canDeleteFile = (file) => {
      // Studenti mogu da brišu samo svoje fajlove
      if (user.value?.rola === 'student') {
        return file.uploader_id === user.value?.id
      }
      // Profesori mogu da brišu bilo koji fajl u sobi
      if (user.value?.rola === 'profesor') {
        return true
      }
      return false
    }
    
    // formatDate je importovan iz utils/dateUtils.js
    
    onMounted(() => {
      loadRoomInfo()
      loadFiles()
    })
    
    return {
      roomId,
      roomInfo,
      roomLoading,
      roomError,
      files,
      loading,
      filesError,
      uploadLoading,
      uploadError,
      uploadSuccess,
      selectedFile,
      fileInput,
      user,
      isRoomCreator,
      loadRoomInfo,
      loadFiles,
      refreshFiles,
      handleFileSelect,
      handleUpload,
      downloadFile,
      deleteFile,
      deleteRoom,
      leaveRoom,
      canDeleteFile,
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

.table th {
  border-top: none;
  font-weight: 600;
}

.btn-group .btn {
  margin-right: 5px;
}

.btn-group .btn:last-child {
  margin-right: 0;
}
</style>
