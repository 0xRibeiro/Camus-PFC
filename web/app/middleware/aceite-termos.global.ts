export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()

  if (!auth.isAuthenticated) {
    return
  }

  if (to.path === '/aceite-termos') {
    return
  }

  if (auth.aceiteTermos === false) {
    return navigateTo('/aceite-termos')
  }
})
