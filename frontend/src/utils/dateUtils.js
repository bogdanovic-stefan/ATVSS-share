export function formatDate(dateString) {
  if (!dateString) return 'N/A'
  
  try {
    const date = new Date(dateString)
    return date.toLocaleString('sr-RS')
  } catch (error) {
    return 'N/A'
  }
}

export function formatDateShort(dateString) {
  if (!dateString) return 'N/A'
  
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('sr-RS')
  } catch (error) {
    return 'N/A'
  }
}
















