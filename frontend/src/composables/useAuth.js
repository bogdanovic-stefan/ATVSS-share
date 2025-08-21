import { computed } from 'vue'
import { useStore } from 'vuex'

export function useAuth() {
  const store = useStore()
  
  const user = computed(() => store.getters.user)
  const isAuthenticated = computed(() => store.getters.isAuthenticated)
  const isProfessor = computed(() => user.value?.rola === 'profesor')
  const isStudent = computed(() => user.value?.rola === 'student')
  
  const logout = () => {
    store.dispatch('logout')
  }
  
  return {
    user,
    isAuthenticated,
    isProfessor,
    isStudent,
    logout
  }
}
















