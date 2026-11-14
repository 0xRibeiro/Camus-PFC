import type { GrupoRead, RoleUsuario } from '~/types/generated'

// com roles: definePageMeta({ middleware: 'role', roles: ['author', 'admin'] })
// sem roles: definePageMeta({ middleware: 'role' }) -> so exige estar logado, qualquer papel
export default defineNuxtRouteMiddleware(async (to) => {
  const roles = to.meta.roles as RoleUsuario[] | undefined
  const auth = useAuthStore()

  if (!auth.isAuthenticated) {
    return navigateTo('/login')
  }

  if (!roles) return

  // se a rota tem roles, verifica se o usuario logado tem uma delas, senao redireciona para a home
  const grupoId = to.params.grupoId
  if (grupoId) {
    try {
      const api = useApi()
      const grupo: GrupoRead = await api(`/grupos/${grupoId}`)
      if (grupo.id_dono !== auth.user?.id) return navigateTo(`/grupos/${grupoId}`)
    }
    catch {
      return navigateTo('/grupos')
    }
    return
  }

  if (!auth.role || !roles.includes(auth.role)) {
    return navigateTo('/')
  }
})
