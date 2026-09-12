import type { RoleUsuario } from '~/types/generated'

// com roles: definePageMeta({ middleware: 'role', roles: ['author', 'admin'] })
// sem roles: definePageMeta({ middleware: 'role' }) -> so exige estar logado, qualquer papel
export default defineNuxtRouteMiddleware((to) => {
  const roles = to.meta.roles as RoleUsuario[] | undefined
  const auth = useAuthStore()

  if (!auth.isAuthenticated) {
    return navigateTo('/login')
  }

  if (roles) {
    if (!auth.role || !roles.includes(auth.role)) {
      return navigateTo('/')
    }
  }
})
