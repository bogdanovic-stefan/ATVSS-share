import { createStore } from 'vuex'
import axios from 'axios'

// Konfiguracija axios-a
axios.defaults.baseURL = '/api'

// Dodavanje tokena u header
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default createStore({
  state: {
    isAuthenticated: !!localStorage.getItem('token'),
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    currentRoom: null
  },
  
  mutations: {
    SET_AUTHENTICATED(state, value) {
      state.isAuthenticated = value
    },
    SET_USER(state, user) {
      state.user = user
    },
    SET_CURRENT_ROOM(state, room) {
      state.currentRoom = room
    }
  },
  
  actions: {
    async login({ commit }, credentials) {
      try {
        const response = await axios.post('/login', credentials)
        const { token, user } = response.data
        
        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(user))
        
        commit('SET_AUTHENTICATED', true)
        commit('SET_USER', user)
        
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Greška pri prijavi' 
        }
      }
    },
    
    async register({ commit }, userData) {
      try {
        await axios.post('/register', userData)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Greška pri registraciji' 
        }
      }
    },
    
    async updateProfile({ commit }, profileData) {
      try {
        console.log('Sending profile data:', profileData)
        await axios.put('/profile', profileData)
        
        // Ažuriranje korisnika u store-u
        const updatedUser = { ...this.state.user, ...profileData }
        localStorage.setItem('user', JSON.stringify(updatedUser))
        commit('SET_USER', updatedUser)
        
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Greška pri ažuriranju profila' 
        }
      }
    },
    
    async createRoom({ commit }, roomData) {
      try {
        const response = await axios.post('/rooms', roomData)
        return { success: true, roomId: response.data.room_id }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Greška pri kreiranju sobe' 
        }
      }
    },
    
    async joinRoom({ commit }, sifra) {
      try {
        const response = await axios.post('/rooms/join', { sifra })
        return { 
          success: true, 
          roomId: response.data.room_id,
          roomName: response.data.room_name
        }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Greška pri pridruživanju sobi' 
        }
      }
    },
    
    async getRoomInfo({ commit }, roomId) {
      try {
        const response = await axios.get(`/rooms/${roomId}`)
        return { success: true, room: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Greška pri učitavanju informacija o sobi' 
        }
      }
    },
    
    async getRoomFiles({ commit }, roomId) {
      try {
        const response = await axios.get(`/rooms/${roomId}/files`)
        return { success: true, files: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Greška pri učitavanju fajlova' 
        }
      }
    },
    
    async uploadFile({ commit }, { roomId, file }) {
      try {
        const formData = new FormData()
        formData.append('file', file)
        
        await axios.post(`/rooms/${roomId}/files`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Greška pri upload-u fajla' 
        }
      }
    },
    
    async deleteFile({ commit }, fileId) {
      try {
        await axios.delete(`/files/${fileId}`)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Greška pri brisanju fajla' 
        }
      }
    },
    
    async downloadFile({ commit }, fileId) {
      try {
        const response = await axios.get(`/files/${fileId}/download`, {
          responseType: 'blob'
        })
        
        // Kreiranje linka za download
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        
        // Pokušaj da dobiješ originalno ime fajla iz header-a
        const contentDisposition = response.headers['content-disposition']
        let filename = 'fajl'
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/)
          if (filenameMatch) {
            filename = filenameMatch[1]
          }
        }
        
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        return { success: true }
      } catch (error) {
        console.error('Greška pri preuzimanju fajla:', error)
        return { 
          success: false, 
          error: error.response?.data?.error || 'Greška pri preuzimanju fajla' 
        }
      }
    },
    
    async leaveRoom({ commit }, roomId) {
      try {
        await axios.post(`/rooms/${roomId}/leave`)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Greška pri napuštanju sobe' 
        }
      }
    },
    
    async deleteRoom({ commit }, roomId) {
      try {
        await axios.delete(`/rooms/${roomId}`)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Greška pri brisanju sobe' 
        }
      }
    },
    
    async getUserRooms({ commit }) {
      try {
        console.log('Store: Getting user rooms...')
        const response = await axios.get('/user/rooms')
        console.log('Store: User rooms response:', response.data)
        return { success: true, rooms: response.data }
      } catch (error) {
        console.error('Store: Error getting user rooms:', error)
        return { 
          success: false, 
          error: error.response?.data?.error || 'Greška pri učitavanju soba' 
        }
      }
    },
    
    logout({ commit }) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      commit('SET_AUTHENTICATED', false)
      commit('SET_USER', null)
      commit('SET_CURRENT_ROOM', null)
    }
  },
  
  getters: {
    isAuthenticated: state => state.isAuthenticated,
    user: state => state.user,
    currentRoom: state => state.currentRoom
  }
})
