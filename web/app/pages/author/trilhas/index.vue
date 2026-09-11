<template>
  <div>
    <!-- cabecalho: titulo + descricao curta + contador de trilhas -->
    <div class="flex items-center justify-between mb-4">
      <div>
        <h1 class="text-xl font-semibold">
          Trilhas
        </h1>
        <p class="text-sm text-muted">
          Cadastre uma trilha e clique nela para montar a jornada de módulos e conteúdos.
        </p>
      </div>

      <UBadge color="secondary" variant="soft" size="xl">
        {{ trilhas.length }} trilha{{ trilhas.length === 1 ? '' : 's' }}
      </UBadge>
    </div>

    <UInput
      v-model="busca"
      icon="i-lucide-search"
      placeholder="Buscar trilha..."
      class="w-full mb-4"
    />

    <!-- spinner enquanto busca as trilhas -->
    <div v-if="loading" class="flex justify-center py-12">
      <UIcon name="i-lucide-loader-circle" class="size-6 animate-spin" />
    </div>

    <!--
      grid com 1 TrilhaCard por trilha, mais o botao de "cadastrar" no final.

      :modulos-count e :conteudos-count sao props indo PRA DENTRO do componente
      (a pagina calculou essas contagens, o card so mostra).

      @edit e @delete sao o caminho contrario: eventos vindo DE DENTRO do componente
      pra fora. o TrilhaCard n sabe abrir modal nem chamar api - ele so avisa
      "cliquei em editar" ou "cliquei em excluir", e aqui na pagina a gente decide
      o que fazer com esse aviso (abrirEditar / onDelete)
    -->
    <UPageGrid v-else>
      <TrilhaCard
        v-for="trilha in trilhasFiltradas"
        :key="trilha.id"
        :trilha="trilha"
        :modulos-count="contarModulos(trilha.id)"
        :conteudos-count="contarConteudos(trilha.id)"
        @edit="abrirEditar(trilha)"
        @delete="onDelete(trilha)"
      />

      <UButton
        icon="i-lucide-plus"
        label="Cadastrar trilha"
        color="neutral"
        variant="outline"
        block
        class="h-full min-h-40"
        @click="abrirCriar()"
      />
    </UPageGrid>

    <!--
      v-model:open="showModal" liga o estado "showModal" daqui com o defineModel('open')
      que existe dentro do TrilhaFormModal - os dois lados sempre ficam sincronizados,
      em qualquer direcao (a pagina fecha o modal fazendo showModal.value = false,
      e o modal tambem pode fechar sozinho por dentro, refletindo aqui fora).

      :trilha="editandoTrilha" e o que diz ao modal se e "criar" (null) ou "editar"
      (a trilha escolhida). @submit e o aviso que o modal manda quando o formulario
      ja foi validado e a pessoa quer salvar - so ai que a pagina chama a api de verdade
    -->
    <TrilhaFormModal
      v-model:open="showModal"
      :trilha="editandoTrilha"
      :saving="saving"
      @submit="onSubmitForm"
    />
  </div>
</template>

<script setup lang="ts">
// TrilhaRead vem do types.gen.ts, gerado a partir da resposta real da api (TrilhaRead
// no back, em python). n escrevemos esse tipo na mao - ele ja reflete exatamente os
// campos que a api devolve (id, titulo, descricao, foto, is_active), e se o back
// mudar um campo, esse tipo atualiza sozinho quando a gente roda o comando de gerar
import type { TrilhaRead } from '~/types/generated'

// so author/admin acessam essa pagina
definePageMeta({ middleware: 'role', roles: ['author', 'admin'] })

const toast = useToast()

const trilhas = ref<TrilhaRead[]>([])
const loading = ref(true)

const busca = ref('')

// computed recalcula sozinho toda vez que "trilhas" ou "busca" mudam
const trilhasFiltradas = computed(() => {
  const resultado: TrilhaRead[] = []
  for (const trilha of trilhas.value) {
    if (trilha.titulo.toLowerCase().includes(busca.value.toLowerCase())) {
      resultado.push(trilha)
    }
  }
  return resultado
})

// contagem de modulos/conteudos por trilha, pro rodape do card
const contagem = ref({
  modulos: new Map<number, number>(),
  conteudos: new Map<number, number>(),
})

// Map.get devolve undefined se a chave n existir - essas 2 funcoes so tratam
// esse caso e devolvem 0 no lugar, pra n espalhar esse "if" pelo template
function contarModulos(trilhaId: number) {
  const total = contagem.value.modulos.get(trilhaId)
  if (total === undefined) return 0
  return total
}

function contarConteudos(trilhaId: number) {
  const total = contagem.value.conteudos.get(trilhaId)
  if (total === undefined) return 0
  return total
}

async function fetchTrilhas() {
  loading.value = true
  const api = useApi()

  const [trilhasRes, modulosRes, conteudosRes] = await Promise.all([
    api('/trilhas'),
    api('/modulos'),
    api('/conteudos'),
  ])
  trilhas.value = trilhasRes.data

  const modulosPorTrilha = new Map<number, number>()
  // guarda de qual trilha cada modulo e, pra depois somar o conteudo na trilha certa
  const trilhaDoModulo = new Map<number, number>()

  for (const modulo of modulosRes.data) {
    let totalModulos = modulosPorTrilha.get(modulo.trilha_id)
    if (totalModulos === undefined) totalModulos = 0
    modulosPorTrilha.set(modulo.trilha_id, totalModulos + 1)

    trilhaDoModulo.set(modulo.id, modulo.trilha_id)
  }

  const conteudosPorTrilha = new Map<number, number>()
  for (const conteudo of conteudosRes.data) {
    const trilhaId = trilhaDoModulo.get(conteudo.modulo_id)
    if (trilhaId === undefined) continue

    let totalConteudos = conteudosPorTrilha.get(trilhaId)
    if (totalConteudos === undefined) totalConteudos = 0
    conteudosPorTrilha.set(trilhaId, totalConteudos + 1)
  }

  contagem.value = { modulos: modulosPorTrilha, conteudos: conteudosPorTrilha }
  loading.value = false
}

// busca assim que a pagina abre
onMounted(fetchTrilhas)

async function onDelete(trilha: TrilhaRead) {
  // apaga em cascata no back: leva modulo e conteudo junto, por isso confirma antes
  const confirmado = confirm(`Excluir a trilha "${trilha.titulo}"? Isso apaga todos os módulos e conteúdos dela também.`)
  if (!confirmado) return

  try {
    const api = useApi()
    await api(`/trilhas/${trilha.id}`, { method: 'DELETE' })

    // monta a lista de novo, sem a trilha excluida
    const restantes: TrilhaRead[] = []
    for (const t of trilhas.value) {
      if (t.id !== trilha.id) restantes.push(t)
    }
    trilhas.value = restantes
  }
  catch {
    toast.add({ title: 'Não foi possível excluir a trilha', color: 'error' })
  }
}

const showModal = ref(false)
const saving = ref(false)

// null = modo criar. preenchido = modo editar (repassado como prop pro TrilhaFormModal)
const editandoTrilha = ref<TrilhaRead | null>(null)

function abrirCriar() {
  editandoTrilha.value = null
  showModal.value = true
}

function abrirEditar(trilha: TrilhaRead) {
  editandoTrilha.value = trilha
  showModal.value = true
}

// isso aqui roda quando o TrilhaFormModal emite "submit" - o formulario ja foi
// validado la dentro do componente, aqui a gente so decide POST (criar) ou PATCH
// (editar) e atualiza a lista local, sem precisar buscar tudo do back de novo
async function onSubmitForm(dados: { titulo: string, foto?: string | null, is_active: boolean }) {
  saving.value = true
  try {
    const api = useApi()

    if (editandoTrilha.value) {
      // o PATCH do fastcrud n devolve o item atualizado (volta vazio), entao
      // atualiza a lista local com os dados que a gente ja tem, sem depender da resposta
      await api(`/trilhas/${editandoTrilha.value.id}`, {
        method: 'PATCH',
        body: dados,
      })

      let antiga: TrilhaRead | undefined
      for (const t of trilhas.value) {
        if (t.id === editandoTrilha.value.id) antiga = t
      }
      if (antiga) Object.assign(antiga, dados)
    }
    else {
      // is_active n existe no TrilhaCreate do back (toda trilha nasce inativa),
      // entao monta o corpo do POST so com o que ele aceita
      const dadosCriacao = { titulo: dados.titulo, foto: dados.foto }
      const nova = await api('/trilhas', { method: 'POST', body: dadosCriacao })
      trilhas.value.push(nova)
    }

    showModal.value = false
  }
  catch {
    toast.add({
      title: editandoTrilha.value ? 'Não foi possível salvar a trilha' : 'Não foi possível criar a trilha',
      color: 'error',
    })
  }
  finally {
    saving.value = false
  }
}
</script>
