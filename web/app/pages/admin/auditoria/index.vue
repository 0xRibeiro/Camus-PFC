<template>
  <div>
    <CamusBanner
      titulo="Auditoria"
      imagem="/papeis-de-parede/avulsos/naufragio.webp"
    />

    <div class="flex flex-wrap items-end gap-3 mb-4">
      <UFormField label="Período">
        <AuditoriaFiltroPeriodo
          v-model:periodo="periodo"
          class="w-64"
        />
      </UFormField>

      <UFormField label="Entidades">
        <!-- bolinha com a cor da entidade, a mesma da tabela -->
        <USelect
          v-model="entidades"
          :items="opcoesEntidade"
          multiple
          placeholder="Todas"
          class="w-64"
        >
          <template #item-leading="{ item }">
            <span
              class="size-2.5 rounded-full"
              :class="item.ponto"
            />
          </template>
        </USelect>
      </UFormField>

      <UFormField label="Usuários">
        <!-- ignore-filter: quem filtra e o back, o select so mostra o q voltou -->
        <USelectMenu
          v-model="usuarioIds"
          v-model:search-term="termoUsuario"
          :items="opcoesUsuario"
          value-key="value"
          multiple
          placeholder="Todos"
          :search-input="{ placeholder: 'Digite o nome, e-mail ou id...' }"
          :loading="buscandoUsuarios"
          ignore-filter
          class="w-72"
        >
          <template #item-leading="{ item }">
            <UsuarioAvatar
              :avatar="item.usuario.avatar"
              :cor-fundo="item.usuario.cor_fundo"
              :tamanho="20"
            />
          </template>
        </USelectMenu>
      </UFormField>

      <!-- inverte a ordem, quem ordena e o back pra valer em todas as paginas -->
      <UTooltip :text="antigosPrimeiro ? 'Mais antigos primeiro' : 'Mais novos primeiro'">
        <UButton
          :icon="antigosPrimeiro ? 'i-lucide-arrow-up-narrow-wide' : 'i-lucide-arrow-down-wide-narrow'"
          aria-label="Inverter ordem"
          color="neutral"
          variant="outline"
          @click="antigosPrimeiro = !antigosPrimeiro"
        />
      </UTooltip>

      <!-- busca de novo com os msm filtros e na msm pagina, pra ver o q entrou depois -->
      <UTooltip text="Atualizar">
        <UButton
          icon="i-lucide-refresh-cw"
          aria-label="Atualizar"
          color="neutral"
          variant="outline"
          :loading="loading"
          @click="fetchLogs"
        />
      </UTooltip>

    </div>

    <!-- embaixo dos filtros, so aparece qnd algum saiu do padrao -->
    <div
      v-if="filtrosAlterados"
      class="-mt-2 mb-4"
    >
      <UButton
        label="Limpar"
        icon="i-lucide-filter-x"
        color="error"
        variant="soft"
        size="sm"
        @click="limparFiltros"
      />
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
import { getLocalTimeZone, today } from '@internationalized/date'
import type { CalendarDate } from '@internationalized/date'
import type { Periodo } from '~/composables/useDashboard'
import type { LogAuditoriaRead, UsuarioAdminRead } from '~/types/generated'

definePageMeta({ middleware: 'role', roles: ['admin'] })

const logs = ref<LogAuditoriaRead[]>([])
const loading = ref(true)

// ------- periodo: por padrao so hoje
const hoje = today(getLocalTimeZone())
// shallowRef pq o ref desmonta o tipo da CalendarDate. o calendario sempre troca o objeto todo
const periodo = shallowRef<Periodo>({ start: hoje, end: hoje })

// comeco do dia no fuso de quem ta vendo, em ISO pro back
function inicioDoDia(dia: CalendarDate) {
  return dia.toDate(getLocalTimeZone()).toISOString()
}

// ------- entidades: vazio = todas
const entidades = ref<string[]>([])

const opcoesEntidade = computed(() => {
  const opcoes: { label: string, value: string, ponto: string }[] = []
  for (const item of ENTIDADES_AUDITORIA) {
    opcoes.push({ label: item.label, value: item.value, ponto: item.ponto })
  }
  return opcoes
})

// ------- usuarios: so busca no back quando digita, no maximo 20. vazio = todos
const usuarioIds = ref<number[]>([])
const termoUsuario = ref('')
const usuariosEncontrados = ref<UsuarioAdminRead[]>([])
const buscandoUsuarios = ref(false)
// guarda os escolhidos pra eles continuarem aparecendo no select qnd a busca muda
const usuariosEscolhidos = ref<UsuarioAdminRead[]>([])

async function buscarUsuarios() {
  const termo = termoUsuario.value.trim()
  // id pode ter 1 digito so, nome precisa de 2 letras
  const ehId = /^\d+$/.test(termo)
  if (!termo || (!ehId && termo.length < 2)) {
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

// escolhidos primeiro, depois o resto do q a busca achou
const opcoesUsuario = computed(() => {
  const opcoes: { label: string, value: number, usuario: UsuarioAdminRead }[] = []
  const jaTem = new Set<number>()
  for (const usuario of [...usuariosEscolhidos.value, ...usuariosEncontrados.value]) {
    if (jaTem.has(usuario.id)) continue
    jaTem.add(usuario.id)
    opcoes.push({ label: `${usuario.id} - ${usuario.username}`, value: usuario.id, usuario })
  }
  return opcoes
})

// monta a lista dos escolhidos a partir dos ids, olhando no q ja tinha e na busca
watch(usuarioIds, (ids) => {
  const escolhidos: UsuarioAdminRead[] = []
  for (const id of ids) {
    for (const usuario of [...usuariosEscolhidos.value, ...usuariosEncontrados.value]) {
      if (usuario.id === id) {
        escolhidos.push(usuario)
        break
      }
    }
  }
  usuariosEscolhidos.value = escolhidos
})

// ------- ordem: por padrao o mais novo primeiro
const antigosPrimeiro = ref(false)

// ------- limpar: volta pro padrao (hoje, todas as entidades, todos os usuarios, mais novo primeiro)
const filtrosAlterados = computed(() => {
  const { start, end } = periodo.value
  const soHoje = !!start && !!end && start.compare(hoje) === 0 && end.compare(hoje) === 0
  return !soHoje || !!entidades.value.length || !!usuarioIds.value.length || antigosPrimeiro.value
})

function limparFiltros() {
  periodo.value = { start: hoje, end: hoje }
  entidades.value = []
  usuarioIds.value = []
  antigosPrimeiro.value = false
}

// ------- busca dos logs
const itensPorPagina = 10
const pagina = ref(1)

async function fetchLogs() {
  const { start, end } = periodo.value
  // no meio da escolha do intervalo o calendario fica sem fim, espera fechar
  if (!start || !end) return

  loading.value = true
  const api = useApi()
  const offset = (pagina.value - 1) * itensPorPagina

  logs.value = await api('/admin/auditoria', {
    query: {
      limite: itensPorPagina,
      offset,
      entidades: entidades.value.length ? entidades.value : undefined,
      usuario_ids: usuarioIds.value.length ? usuarioIds.value : undefined,
      desde: inicioDoDia(start),
      // ate o comeco do dia seguinte, assim o ultimo dia entra inteiro
      ate: inicioDoDia(end.add({ days: 1 })),
      antigos_primeiro: antigosPrimeiro.value,
    },
  })

  loading.value = false
}

onMounted(fetchLogs)

// muda filtro -> volta pra pagina 1 e busca de novo
watch([periodo, entidades, usuarioIds, antigosPrimeiro], () => {
  pagina.value = 1
  fetchLogs()
}, { deep: true })

function paginaAnterior() {
  pagina.value -= 1
  fetchLogs()
}

function proximaPagina() {
  pagina.value += 1
  fetchLogs()
}
</script>
