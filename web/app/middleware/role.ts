import type { RoleUsuario } from '~/types/generated'

// usa assim numa pagina: definePageMeta({ middleware: 'role', roles: ['author', 'admin'] })
export default defineNuxtRouteMiddleware((to) => {
  const roles = to.meta.roles as RoleUsuario[] | undefined
  if (!roles) return // pagina sem essa opcao configurada, n restringe nada

  const auth = useAuthStore()

  if (!auth.isAuthenticated) {
    return navigateTo('/login')
  }

  if (!auth.role || !roles.includes(auth.role)) {
    return navigateTo('/')
  }
})
