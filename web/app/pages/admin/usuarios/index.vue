<template>
  <div>
    <CamusBanner
      titulo="Usuários"
      imagem="/papeis-de-parede/avulsos/lontra-marinha.webp"
    />

    <UsuarioOnlineList
      :usuarios="usuariosOnline"
      :loading="loadingOnline"
    />

    <!-- lista de todos, o cadastro de author/admin abre no modal (aluno se cadastra sozinho) -->
    <UCard :ui="{ body: 'p-0 sm:p-0' }">
      <template #header>
        <div class="flex items-center justify-between gap-3">
          <div class="flex items-center gap-2">
            <h2 class="font-medium">
              Usuários
            </h2>
            <UBadge
              color="neutral"
              variant="soft"
            >
              {{ usuarios.length }}
            </UBadge>
          </div>

          <UButton
            label="Novo usuário"
            icon="i-lucide-user-plus"
            @click="criando = true"
          />
        </div>

        <!-- busca e filtro por papel -->
        <div class="mt-4 flex flex-wrap items-center gap-3">
          <UInput
            v-model="busca"
            icon="i-lucide-search"
            placeholder="Buscar por usuário ou email..."
            class="w-full min-w-0 sm:flex-1"
          />

          <div class="flex flex-wrap items-center gap-2">
            <UButton
              v-for="papel in papeis"
              :key="papel.role"
              :label="papel.titulo"
              :icon="papel.icone"
              :color="papel.cor"
              :variant="papeisFiltro.includes(papel.role) ? 'solid' : 'soft'"
              size="sm"
              @click="alternarPapel(papel.role)"
            />

            <USeparator
              orientation="vertical"
              class="h-6"
            />

            <!-- ativos x desativados, um clique troca -->
            <UButton
              :label="mostrarAtivos ? 'Ativos' : 'Desativados'"
              :icon="mostrarAtivos ? 'i-lucide-user-check' : 'i-lucide-user-x'"
              :color="mostrarAtivos ? 'success' : 'error'"
              variant="subtle"
              size="sm"
              class="w-32 justify-center"
              @click="alternarStatus"
            />
          </div>
        </div>

        <!-- em linha propria pra n empurrar os botoes de papel, alinhado com eles -->
        <div
          v-if="filtrosAtivos"
          class="mt-2 flex justify-end"
        >
          <UButton
            label="Limpar filtros"
            icon="i-lucide-x"
            color="neutral"
            variant="link"
            size="sm"
            class="px-0"
            @click="limparFiltros"
          />
        </div>
      </template>

      <div
        v-if="loading"
        class="flex justify-center py-12"
      >
        <UIcon
          name="i-lucide-loader-circle"
          class="size-6 animate-spin"
        />
      </div>

      <!-- um bloco por papel: admin, autor e aluno -->
      <div
        v-else
        class="divide-y divide-default"
      >
        <section
          v-for="grupo in grupos"
          :key="grupo.role"
        >
          <div
            class="flex items-center gap-2 border-l-4 px-4 py-3"
            :class="grupo.estilo.faixa"
          >
            <UIcon
              :name="grupo.icone"
              class="size-5"
              :class="grupo.estilo.texto"
            />
            <h3
              class="font-semibold"
              :class="grupo.estilo.texto"
            >
              {{ grupo.titulo }}
            </h3>
            <UBadge
              :color="grupo.cor"
              variant="soft"
              size="sm"
            >
              {{ grupo.usuarios.length }}
            </UBadge>
          </div>

          <p
            v-if="!grupo.usuarios.length"
            class="px-4 py-4 text-sm text-muted"
          >
            <template v-if="busca">
              Ninguém encontrado nesse papel.
            </template>
            <template v-else>
              Nenhum usuário {{ mostrarAtivos ? 'ativo' : 'desativado' }} nesse papel.
            </template>
          </p>

          <template v-else>
            <!-- UTable = tabela pronta do nuxt ui, so precisa de data + columns. linhas zebradas -->
            <UTable
              :data="paginaDoGrupo(grupo.role, grupo.usuarios)"
              :columns="columns"
              :ui="{ base: 'table-fixed', tr: 'even:bg-elevated/60' }"
            >
              <template #username-cell="{ row }">
                <div class="flex items-center gap-2">
                  <UsuarioAvatar
                    :avatar="row.original.avatar"
                    :cor-fundo="row.original.cor_fundo"
                    :tamanho="28"
                  />
                  <span class="font-medium text-highlighted">{{ row.original.username }}</span>
                </div>
              </template>

              <!-- a propria conta e as ja excluidas n tem botao -->
              <template #acoes-cell="{ row }">
                <UTooltip
                  v-if="row.original.id !== auth.user?.id && !row.original.deletado_em"
                  text="Excluir conta"
                >
                  <UButton
                    icon="i-lucide-trash-2"
                    aria-label="Excluir conta"
                    color="error"
                    variant="ghost"
                    size="sm"
                    @click="abrirExcluir(row.original)"
                  />
                </UTooltip>
              </template>

              <template #ultimo_acesso_em-cell="{ row }">
                <span :class="row.original.ultimo_acesso_em ? 'text-toned' : 'text-dimmed italic'">
                  {{ formatarAcesso(row.original.ultimo_acesso_em) }}
                </span>
              </template>

              <!-- excluida > ativa > desativada -->
              <template #is_active-cell="{ row }">
                <UBadge
                  v-if="row.original.deletado_em"
                  label="Excluída"
                  icon="i-lucide-trash-2"
                  color="neutral"
                  variant="subtle"
                />
                <UBadge
                  v-else-if="row.original.is_active"
                  label="Ativo"
                  icon="i-lucide-circle-check"
                  color="success"
                  variant="subtle"
                />
                <UBadge
                  v-else
                  label="Desativado"
                  icon="i-lucide-circle-x"
                  color="error"
                  variant="subtle"
                />
              </template>

              <!-- email vem mascarado, o olhinho busca o de verdade e o back grava na auditoria -->
              <template #email-cell="{ row }">
                <div class="flex items-center gap-1">
                  <span :class="{ 'font-mono text-xs': !revelados[row.original.id] }">
                    {{ revelados[row.original.id] ?? row.original.email }}
                  </span>
                  <UTooltip :text="revelados[row.original.id] ? 'Esconder email' : 'Ver email (fica registrado)'">
                    <UButton
                      :icon="revelados[row.original.id] ? 'i-lucide-eye-off' : 'i-lucide-eye'"
                      :aria-label="revelados[row.original.id] ? 'Esconder email' : 'Ver email'"
                      color="neutral"
                      variant="ghost"
                      size="xs"
                      :loading="revelando === row.original.id"
                      @click="alternarEmail(row.original.id)"
                    />
                  </UTooltip>
                </div>
              </template>
            </UTable>

            <!-- cada papel pagina sozinho -->
            <div
              v-if="grupo.usuarios.length > POR_PAGINA"
              class="flex justify-center border-t border-default px-4 py-3"
            >
              <UPagination
                v-model:page="paginas[grupo.role]"
                :total="grupo.usuarios.length"
                :items-per-page="POR_PAGINA"
                size="sm"
              />
            </div>
          </template>
        </section>
      </div>
    </UCard>

    <UsuarioCriarModal
      v-model:open="criando"
      @criado="usuarios.push($event)"
    />

    <UModal
      v-model:open="showDeleteModal"
      title="Excluir conta"
      :description="descricaoExclusao"
      :ui="{ footer: 'justify-end' }"
    >
      <template #footer="{ close }">
        <UButton
          label="Cancelar"
          color="neutral"
          variant="outline"
          @click="close"
        />
        <UButton
          label="Excluir"
          color="error"
          :loading="excluindo"
          @click="confirmarExclusao"
        />
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import type { EmailReveladoRead, UsuarioAdminRead } from '~/types/generated'

// so admin acessa essa pagina
definePageMeta({ middleware: 'role', roles: ['admin'] })

const api = useApi()
const toast = useToast()

const usuarios = ref<UsuarioAdminRead[]>([])
const loading = ref(true)
const busca = ref('')

// a busca roda no back pq o email chega mascarado aqui
async function fetchUsuarios() {
  // GET /admin/usuarios e rota escrita na mao no back (n fastcrud), devolve array direto,
  // sem o { data: [...] } que a gente ve nas rotas de trilha/modulo/conteudo
  const termo = busca.value.trim()
  usuarios.value = await api('/admin/usuarios', { query: termo ? { busca: termo } : undefined })
  loading.value = false
}

// busca assim que a pagina abre, e de novo quando para de digitar
onMounted(fetchUsuarios)
watchDebounced(busca, fetchUsuarios, { debounce: 350 })

// ------- email revelado pelo olhinho, so fica na tela ate esconder
const revelados = ref<Record<number, string>>({})
const revelando = ref<number | null>(null)

async function alternarEmail(id: number) {
  if (revelados.value[id]) {
    const restantes: Record<number, string> = {}
    for (const chave in revelados.value) {
      if (Number(chave) !== id) restantes[Number(chave)] = revelados.value[chave] as string
    }
    revelados.value = restantes
    return
  }

  revelando.value = id
  try {
    const resposta: EmailReveladoRead = await api(`/admin/usuarios/${id}/email`)
    revelados.value = { ...revelados.value, [id]: resposta.email }
  }
  catch {
    toast.add({ title: 'Não foi possível ver o email', color: 'error' })
  }
  finally {
    revelando.value = null
  }
}

const usuariosOnline = ref<UsuarioAdminRead[]>([])
const loadingOnline = ref(true)

// o loading so vale na primeira vez, nas atualizacoes os peixes continuam nadando
async function fetchUsuariosOnline() {
  try {
    usuariosOnline.value = await api('/admin/usuarios/online')
  }
  finally {
    loadingOnline.value = false
  }
}

onMounted(fetchUsuariosOnline)
// quem entrou ou saiu aparece sozinho, a cada 1 minuto
useIntervalFn(fetchUsuariosOnline, 60_000)

// define quais colunas a UTable desenha e o nome de cada uma. accessorKey tem
// que bater com o nome do campo la no UsuarioAdminRead (username, email, is_active).
// largura fixa pra as tabelas dos 3 papeis ficarem alinhadas umas com as outras
const columns: TableColumn<UsuarioAdminRead>[] = [
  { accessorKey: 'username', header: 'Usuário', meta: { class: { th: 'w-[28%]', td: 'truncate' } } },
  { accessorKey: 'email', header: 'Email', meta: { class: { th: 'w-[28%]', td: 'truncate' } } },
  { accessorKey: 'ultimo_acesso_em', header: 'Último acesso', meta: { class: { th: 'w-[20%]' } } },
  { accessorKey: 'is_active', header: 'Status', meta: { class: { th: 'w-[16%]' } } },
  { id: 'acoes', header: '', meta: { class: { th: 'w-[8%]', td: 'text-right' } } },
]

function formatarAcesso(data: string | null | undefined) {
  if (!data) return 'Nunca entrou'
  return new Date(data).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

// ordem dos blocos e a cara de cada um
const papeis = [
  {
    role: 'admin',
    titulo: 'Admins',
    icone: 'i-lucide-shield',
    cor: 'quaternary',
    estilo: { faixa: 'border-quaternary bg-quaternary/10', texto: 'text-quaternary' },
  },
  {
    role: 'author',
    titulo: 'Autores',
    icone: 'i-lucide-pen-tool',
    cor: 'secondary',
    estilo: { faixa: 'border-secondary bg-secondary/10', texto: 'text-secondary' },
  },
  {
    role: 'aluno',
    titulo: 'Alunos',
    icone: 'i-lucide-graduation-cap',
    cor: 'tertiary',
    estilo: { faixa: 'border-tertiary bg-tertiary/10', texto: 'text-tertiary' },
  },
] as const

type Papel = typeof papeis[number]['role']

// ------- filtro por papel e por status
// vazio = mostra todos os papeis
const papeisFiltro = ref<Papel[]>([])
// por padrao so os ativos, clicar troca pros desativados
const mostrarAtivos = ref(true)

function alternarPapel(role: Papel) {
  const restantes: Papel[] = []
  for (const item of papeisFiltro.value) {
    if (item !== role) restantes.push(item)
  }
  if (restantes.length === papeisFiltro.value.length) restantes.push(role)
  papeisFiltro.value = restantes
}

// trocar o status limpa a busca, conta excluida fica com o nome anonimizado
function alternarStatus() {
  mostrarAtivos.value = !mostrarAtivos.value
  busca.value = ''
}

function limparFiltros() {
  busca.value = ''
  papeisFiltro.value = []
  mostrarAtivos.value = true
}

const filtrosAtivos = computed(() => !!busca.value || !!papeisFiltro.value.length || !mostrarAtivos.value)

// a lista ja vem filtrada pela busca do back, aqui so separa por papel
const grupos = computed(() => {
  const resultado = []
  for (const papel of papeis) {
    if (papeisFiltro.value.length && !papeisFiltro.value.includes(papel.role)) continue

    const lista: UsuarioAdminRead[] = []
    for (const usuario of usuarios.value) {
      if (usuario.role === papel.role && usuario.is_active === mostrarAtivos.value) lista.push(usuario)
    }
    resultado.push({ ...papel, usuarios: lista })
  }
  return resultado
})

// ------- paginacao, no maximo 30 por pagina em cada papel
const POR_PAGINA = 30
const paginas = ref<Record<Papel, number>>({ admin: 1, author: 1, aluno: 1 })

watch([busca, papeisFiltro, mostrarAtivos], () => {
  paginas.value = { admin: 1, author: 1, aluno: 1 }
})

function paginaDoGrupo(role: Papel, lista: UsuarioAdminRead[]) {
  const inicio = (paginas.value[role] - 1) * POR_PAGINA
  return lista.slice(inicio, inicio + POR_PAGINA)
}

// abre o modal de cadastro, o novo entra na lista sem buscar tudo de novo
const criando = ref(false)

// ------- exclusao de conta (soft delete no back, a linha vira "Excluída")
const auth = useAuthStore()
const showDeleteModal = ref(false)
const excluindo = ref(false)
const usuarioParaExcluir = ref<UsuarioAdminRead | null>(null)

const descricaoExclusao = computed(() => {
  if (!usuarioParaExcluir.value) return ''
  return `Excluir a conta de "${usuarioParaExcluir.value.username}"? Os dados pessoais são apagados e a pessoa não consegue mais entrar. Não dá pra desfazer.`
})

function abrirExcluir(usuario: UsuarioAdminRead) {
  usuarioParaExcluir.value = usuario
  showDeleteModal.value = true
}

async function confirmarExclusao() {
  if (!usuarioParaExcluir.value) return

  excluindo.value = true
  try {
    await api(`/admin/usuarios/${usuarioParaExcluir.value.id}`, { method: 'DELETE' })
    showDeleteModal.value = false
    // busca de novo pq o back troca nome e email da conta excluida
    await fetchUsuarios()
  }
  catch {
    toast.add({ title: 'Não foi possível excluir a conta', color: 'error' })
  }
  finally {
    excluindo.value = false
  }
}
</script>
