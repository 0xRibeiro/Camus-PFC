<template>
  <div>
    <CamusBanner
      titulo="Auditoria"
      imagem="/papeis-de-parede/avulsos/naufragio.webp"
    />

    <div class="flex flex-wrap items-end gap-3 mb-4">
      <UFormField label="Entidade">
        <!-- bolinha com a cor da entidade, a mesma da tabela -->
        <USelect
          v-model="entidade"
          :items="opcoesEntidade"
          placeholder="Todas"
          class="w-56"
        >
          <template #leading>
            <span
              v-if="entidade"
              class="size-2.5 rounded-full"
              :class="entidadeAuditoria(entidade).ponto"
            />
          </template>
          <template #item-leading="{ item }">
            <span
              class="size-2.5 rounded-full"
              :class="item.ponto"
            />
          </template>
        </USelect>
      </UFormField>

      <!-- busca pelo nome ou pelo id, o label tem os dois -->
      <UFormField label="Usuário">
        <!-- ignore-filter: quem filtra e o back, o select so mostra o q voltou -->
        <USelectMenu
          v-model="usuarioId"
          v-model:search-term="termoUsuario"
          :items="opcoesUsuario"
          value-key="value"
          placeholder="Todos"
          :search-input="{ placeholder: 'Digite o nome ou e-mail...' }"
          :loading="buscandoUsuarios"
          ignore-filter
          class="w-64"
        >
          <template #item-leading="{ item }">
            <UsuarioAvatar
              v-if="item.usuario"
              :avatar="item.usuario.avatar"
              :cor-fundo="item.usuario.cor_fundo"
              :tamanho="20"
            />
          </template>
        </USelectMenu>
      </UFormField>
    </div>

    <div class="rounded-xl bg-default ring ring-default">
      <AuditoriaTable
        :logs="logs"
        :loading="loading"
      />
    </div>

    <div class="flex justify-end gap-2 mt-4">
      <UButton
        label="Anterior"
        variant="outline"
        :disabled="pagina === 1"
        @click="paginaAnterior"
      />
      <UButton
        label="Próxima"
        variant="outline"
        :disabled="logs.length < itensPorPagina"
        @click="proximaPagina"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { LogAuditoriaRead, UsuarioAdminRead } from '~/types/generated'

definePageMeta({ middleware: 'role', roles: ['admin'] })

const logs = ref<LogAuditoriaRead[]>([])
const loading = ref(true)

// ------- select de usuario: so busca no back quando digita, no maximo 20
const usuarioId = ref<number | undefined>(undefined)
const termoUsuario = ref('')
const usuariosEncontrados = ref<UsuarioAdminRead[]>([])
const buscandoUsuarios = ref(false)
// guarda o escolhido pra ele continuar aparecendo no select qnd a busca muda
const usuarioEscolhido = ref<UsuarioAdminRead | null>(null)

async function buscarUsuarios() {
  const termo = termoUsuario.value.trim()
  if (termo.length < 2) {
    usuariosEncontrados.value = []
    return
  }

  buscandoUsuarios.value = true
  try {
    const api = useApi()
    usuariosEncontrados.value = await api('/admin/usuarios', { query: { busca: termo, limite: 20 } })
  }
  finally {
    buscandoUsuarios.value = false
  }
}

watchDebounced(termoUsuario, buscarUsuarios, { debounce: 350 })

type OpcaoUsuario = { label: string, value: number | undefined, usuario?: UsuarioAdminRead }

function opcaoDe(usuario: UsuarioAdminRead): OpcaoUsuario {
  return { label: `${usuario.id} - ${usuario.username}`, value: usuario.id, usuario }
}

// "Todos" primeiro pra dar pra tirar o filtro, depois o escolhido e o resultado da busca
const opcoesUsuario = computed(() => {
  const opcoes: OpcaoUsuario[] = [{ label: 'Todos', value: undefined }]
  if (usuarioEscolhido.value) opcoes.push(opcaoDe(usuarioEscolhido.value))
  for (const usuario of usuariosEncontrados.value) {
    if (usuario.id !== usuarioEscolhido.value?.id) opcoes.push(opcaoDe(usuario))
  }
  return opcoes
})

watch(usuarioId, (id) => {
  if (id === undefined) {
    usuarioEscolhido.value = null
    return
  }
  for (const usuario of usuariosEncontrados.value) {
    if (usuario.id === id) usuarioEscolhido.value = usuario
  }
})

const itensPorPagina = 10
const pagina = ref(1)
const entidade = ref<string | undefined>(undefined)

async function fetchLogs() {
  loading.value = true
  const api = useApi()
  const offset = (pagina.value - 1) * itensPorPagina

  logs.value = await api('/admin/auditoria', {
    query: {
      limite: itensPorPagina,
      offset,
      entidade: entidade.value,
      usuario_id: usuarioId.value,
    },
  })

  loading.value = false
}

onMounted(fetchLogs)

// "Todas" sem cor, o resto vem da lista compartilhada com a tabela
const opcoesEntidade = computed(() => {
  const opcoes: { label: string, value: string | undefined, ponto: string }[] = [
    { label: 'Todas', value: undefined, ponto: '' },
  ]
  for (const item of ENTIDADES_AUDITORIA) {
    opcoes.push({ label: item.label, value: item.value, ponto: item.ponto })
  }
  return opcoes
})

// muda filtro -> volta pra pagina 1 e busca de novo
watch([entidade, usuarioId], () => {
  pagina.value = 1
  fetchLogs()
})

function paginaAnterior() {
  pagina.value -= 1
  fetchLogs()
}

function proximaPagina() {
  pagina.value += 1
  fetchLogs()
}
</script>
