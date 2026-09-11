import type { UsuarioCreate, UsuarioLogin, UsuarioRead } from '~/types/generated'

// store de auth, guarda quem ta logado e os tokens
export const useAuthStore = defineStore('auth', () => {
  const user = ref<UsuarioRead | null>(null) // null = ninguem logado ainda
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value)
  const role = computed(() => user.value?.role ?? null) // ?. evita erro se user for null

  // busca os dados do usuario logado
  async function fetchMe() {
    const api = useApi()
    user.value = await api('/usuarios/me')
  }

  // login so devolve token, entao busca o usuario dps
  async function login(credentials: UsuarioLogin) {
    const api = useApi()
    const tokens = await api('/auth/login', {
      method: 'POST',
      body: credentials,
    })
    accessToken.value = tokens.access_token
    refreshToken.value = tokens.refresh_token
    await fetchMe()
  }

  // registro n devolve token, entao loga logo em seguida com os msm dados
  async function register(data: UsuarioCreate) {
    const api = useApi()
    await api('/auth/register', {
      method: 'POST',
      body: data,
    })
    await login({ email: data.email, password: data.password })
  }

  // null = ninguem renovando agora.
  let renovacaoEmAndamento: Promise<void> | null = null

  async function refresh() {
    // const separada pra n resetar
    const currentRefreshToken = refreshToken.value
    if (!currentRefreshToken) {
      throw new Error('Sem refresh token pra renovar')
    }

    // so comeca chamada nova se n tiver nenhum em andamento
    if (!renovacaoEmAndamento) {
      // funcao criada e chamada na hora (os () no final), pra já disparar a chamada
      renovacaoEmAndamento = (async () => {
        const api = useApi()
        const tokens = await api('/auth/refresh', {
          method: 'POST',
          body: { refresh_token: currentRefreshToken },
        })
        accessToken.value = tokens.access_token
        refreshToken.value = tokens.refresh_token
      })().finally(() => {
        renovacaoEmAndamento = null // libera pra proxima chamada
      })
    }

    return renovacaoEmAndamento
  }

  async function logout() {
    const api = useApi()
    const currentRefreshToken = refreshToken.value
    if (currentRefreshToken) {
      // avisa o back pra invalidar
      await api('/auth/logout', {
        method: 'POST',
        body: { refresh_token: currentRefreshToken },
      }).catch(() => {})
    } // limpa local
    user.value = null
    accessToken.value = null
    refreshToken.value = null
  }

  return { user, accessToken, refreshToken, isAuthenticated, role, login, register, fetchMe, refresh, logout }
}, {
  persist: {
    storage: sessionStorage,
    pick: ['user', 'accessToken', 'refreshToken'], // oq persiste entre reloads
  },
})
