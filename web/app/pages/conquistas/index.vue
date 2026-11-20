<template>
  <div class="flex-1 p-4">
    <div class="mx-auto w-full max-w-6xl space-y-8">
      <CamusBanner
        titulo="Conquistas"
        descricao="Conquistas disponíveis atualmente."
        imagem="/papeis-de-parede/amarelo/conquistas.webp"
        headline="Seu progresso"
        icone="i-lucide-trophy"
      />

      <!-- erro caso as conquistas nao carreguem -->
      <UAlert
        v-if="mensagem_de_erro"
        color="error"
        variant="subtle"
        icon="i-lucide-circle-alert"
        title="Não foi possível carregar as conquistas"
        :description="mensagem_de_erro"
      />

      <!-- parte superior onde fica o resumo -->
      <section class="grid gap-4 sm:grid-cols-3">
        <UCard>
          <p class="text-sm text-muted">Desbloqueadas</p>
          <p class="mt-2 text-3xl font-semibold text-highlighted">
            {{ ids_conquistas_desbloqueadas.size }}
          </p>
        </UCard>
        <UCard>
          <p class="text-sm text-muted">Disponíveis para desbloqueio</p>
          <!-- essa é utilizada para separar as conquistas desbloqueadas das outras -->
          <p class="mt-2 text-3xl font-semibold text-highlighted">
            {{ todasConquistas.length - ids_conquistas_desbloqueadas.size }}
          </p>
        </UCard>
        <UCard>
          <!-- esse progresso é bom para mostrar o quanto falta, principalmente quando tiver muitas conquistas -->
          <p class="text-sm text-muted">Progresso</p>
          <p class="mt-2 text-3xl font-semibold text-highlighted">
            {{ progresso }}%
          </p>
          <UProgress :model-value="progresso" class="mt-3" />
        </UCard>
      </section>

      <div v-if="carregando" class="grid gap-4 sm:grid-cols-2">
        <UCard v-for="indice in 6" :key="indice">
          <div class="flex items-start gap-4">
            <USkeleton class="size-14 rounded-xl" />
            <div class="flex-1 space-y-2">
              <USkeleton class="h-4 w-2/3" />
              <USkeleton class="h-3 w-full" />
              <USkeleton class="h-3 w-1/2" />
            </div>
          </div>
        </UCard>
      </div>

      <UEmpty
        v-else-if="!todasConquistas.length && !mensagem_de_erro"
        icon="i-lucide-trophy"
        title="Nenhuma conquista cadastrada"
        description="As conquistas aparecerão aqui quando estiverem disponíveis."
      />

      <section v-else class="grid gap-4 sm:grid-cols-2">
        <!-- aqui tem o for que passa por todas as conquistas e vai colocando os cards de cada uma -->
        <UCard
          v-for="conquista in conquistasOrdenadas"
          :key="conquista.id"
          :class="ids_conquistas_desbloqueadas.has(conquista.id) ? 'ring-primary/50' : 'opacity-70'"
        >
          <!-- a opacidade muda na linha de cima para distinguir as conquistas desbloqueadas das outras -->
          <div class="flex items-start gap-4">
            <div
              class="flex size-14 shrink-0 items-center justify-center overflow-hidden rounded-xl"
              :class="ids_conquistas_desbloqueadas.has(conquista.id) ? 'bg-primary/10 text-primary' : 'bg-elevated text-muted'"
            >
              <img
                v-if="conquista.imagem_dir"
                :src="conquista.imagem_dir"
                :alt="conquista.titulo"
                class="size-full object-cover"
              >
              <UIcon v-else name="i-lucide-award" class="size-7" />
            </div>

            <div class="min-w-0 flex-1">
              <div class="flex items-start justify-between gap-2">
                <h2 class="font-semibold text-highlighted">{{ conquista.titulo }}</h2>
                <UIcon
                  v-if="ids_conquistas_desbloqueadas.has(conquista.id)"
                  name="i-lucide-circle-check"
                  class="size-5 shrink-0 text-primary"
                  aria-label="Conquista desbloqueada"
                />
                <UIcon
                  v-else
                  name="i-lucide-lock"
                  class="size-4 shrink-0 text-muted"
                  aria-label="Conquista bloqueada"
                />
              </div>
              <p class="mt-2 text-sm leading-5 text-muted">
                {{ conquista.descricao || 'continue utilizando a plataforma para desbloquear.' }}
              </p>
              <!-- caso a conquista não tenha descricão o site coloca uma generica -->
              <div class="mt-3 flex flex-wrap items-center gap-2">
                <UBadge
                  :color="ids_conquistas_desbloqueadas.has(conquista.id) ? 'primary' : 'neutral'"
                  variant="subtle"
                >
                  <!-- em cima tem outro operador ternario que distingue as bloqueadas das desbloqueada -->
                  {{ ids_conquistas_desbloqueadas.has(conquista.id) ? 'Desbloqueada' : 'Bloqueada' }}
                </UBadge>
                <span
                  v-if="datas.get(conquista.id)"
                  class="text-xs text-muted"
                >
                  em {{ formatarData(datas.get(conquista.id)!) }}
                </span>
              </div>
            </div>
          </div>
        </UCard>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ConquistaRead, ConquistaUsuarioRead } from '~/types/generated'

// verifica a role do usuario
definePageMeta({ middleware: 'role' })

// trata as conquistas recebidas da api.
type RespostaListaConquistas = ConquistaRead[] | { data?: ConquistaRead[] }

const api = useApi()
const todasConquistas = ref<ConquistaRead[]>([])
const ids_conquistas_desbloqueadas = ref(new Set<number>())
// id -> quando desbloqueou
const datas = ref(new Map<number, string | null>())
const carregando = ref(true)
const mensagem_de_erro = ref('')

// aqui que faz a conta da porcentagem de conquistas desbloqueadas do usuario
const progresso = computed(() => {
  if (!todasConquistas.value.length) return 0
  return Math.round((ids_conquistas_desbloqueadas.value.size / todasConquistas.value.length) * 100)
})

// desbloqueadas primeiro (mais nova no topo, o back ja manda assim) e as bloqueadas no fim
const conquistasOrdenadas = computed(() => {
  const desbloqueadas: ConquistaRead[] = []
  const bloqueadas: ConquistaRead[] = []
  for (const conquista of todasConquistas.value) {
    if (!ids_conquistas_desbloqueadas.value.has(conquista.id)) bloqueadas.push(conquista)
  }
  for (const id of datas.value.keys()) {
    const conquista = todasConquistas.value.find(item => item.id === id)
    if (conquista) desbloqueadas.push(conquista)
  }
  return [...desbloqueadas, ...bloqueadas]
})

function formatarData(data: string) {
  return new Date(data).toLocaleDateString('pt-BR')
}

function obterItens(resposta: RespostaListaConquistas) {
  return Array.isArray(resposta) ? resposta : resposta.data || []
}

// usa as rotass disponiveis para pegar as conquistas e ver quais o usuario ja tem
async function buscarConquistas() {
  carregando.value = true
  mensagem_de_erro.value = ''

  try {
    const [resposta_todas_conquistas, resposta_conquistas_desbloqueadas] = await Promise.all([
      api('/conquistas') as Promise<RespostaListaConquistas>,
      api('/usuarios/me/conquistas') as Promise<ConquistaUsuarioRead[]>,
    ])

    todasConquistas.value = obterItens(resposta_todas_conquistas)
    ids_conquistas_desbloqueadas.value = new Set(resposta_conquistas_desbloqueadas.map(conquista => conquista.id))

    // map guarda a ordem q chegou, entao serve pra ordenar tbm
    const novasDatas = new Map<number, string | null>()
    for (const conquista of resposta_conquistas_desbloqueadas) {
      novasDatas.set(conquista.id, conquista.desbloqueada_em ?? null)
    }
    datas.value = novasDatas
    carregando.value = false
  }
  catch {
    mensagem_de_erro.value = 'Tente novamente em alguns instantes.'
    carregando.value = false
  }
}

// busca as conquistas assim que carrega a pagina
onMounted(buscarConquistas)
</script>
