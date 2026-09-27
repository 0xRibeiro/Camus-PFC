export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()

  if (!auth.isAuthenticated) {
    return
  }

  // Páginas públicas dos documentos
  if (
    to.path === '/termos-de-uso' ||
    to.path === '/politica-de-privacidade'
  ) {
    return
  }

  // A própria página de aceite pode ser acessada sem redirecionamento
  if (to.path === '/aceite-termos') {
    return
  }

  if (auth.aceiteTermos === null) {
    try {
      await auth.fetchAceiteTermos()
    } catch {
      return
    }
  }

  if (auth.aceiteTermos === false) {
    return navigateTo('/aceite-termos')
  }
})