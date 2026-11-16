<template>
  <UCard>
    <template #header>
      <div class="flex items-center gap-3">
        <div class="flex size-10 items-center justify-center rounded-full bg-violet-500/10 text-violet-500 ring ring-violet-500/25 ring-inset">
          <UIcon
            name="i-lucide-users"
            class="size-5"
          />
        </div>

        <div>
          <h2 class="font-medium">
            Quem cuida desse aquário
          </h2>
          <p class="text-xs text-muted">
            {{ membros.length }} {{ membros.length === 1 ? 'pessoa' : 'pessoas' }}
          </p>
        </div>
      </div>
    </template>

    <div class="space-y-4">
      <div
        v-if="carregando"
        class="space-y-3"
      >
        <USkeleton
          v-for="indice in 2"
          :key="indice"
          class="h-12 w-full"
        />
      </div>

      <ul
        v-else
        class="divide-y divide-default"
      >
        <li
          v-for="membro in membros"
          :key="membro.username"
          class="flex items-center gap-3 py-2.5 first:pt-0 last:pb-0"
        >
          <UsuarioAvatar
            :avatar="membro.avatar"
            :cor-fundo="membro.cor_fundo"
            :tamanho="40"
          />

          <p class="min-w-0 flex-1 truncate font-medium">
            {{ membro.username }}
          </p>

          <UBadge
            :color="papeis[membro.papel].cor"
            :icon="papeis[membro.papel].icone"
            :label="papeis[membro.papel].nome"
            variant="subtle"
          />
        </li>
      </ul>

      <div
        v-if="papel === 'dono'"
        class="space-y-2 rounded-lg bg-elevated/50 p-4"
      >
        <p class="text-sm text-muted">
          Gere um convite pra alguém acompanhar o aquário só como leitor. Ele vale por 15 minutos.
        </p>

        <UButton
          :label="convite ? 'Gerar outro convite' : 'Gerar convite'"
          icon="i-lucide-user-plus"
          :loading="gerando"
          @click="gerarConvite"
        />

        <div
          v-if="convite"
          class="space-y-2"
        >
          <UFormField label="Código de convite">
            <div class="flex flex-wrap gap-2">
              <UInput
                :model-value="convite.convite"
                readonly
                class="w-full sm:w-64"
              />
              <UButton
                label="Copiar"
                icon="i-lucide-copy"
                color="neutral"
                variant="outline"
                :disabled="segundosRestantes === 0"
                @click="copiarConvite"
              />
            </div>
          </UFormField>

          <p class="text-sm text-muted">
            {{ segundosRestantes > 0 ? `Expira em ${tempoRestante}.` : 'Este convite expirou. Gere outro.' }}
          </p>
        </div>
      </div>

      <UButton
        v-else
        label="Sair do aquário"
        icon="i-lucide-log-out"
        color="error"
        variant="outline"
        :loading="saindo"
        @click="sair"
      />
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { FetchError } from 'ofetch'
import type { ConviteAquarioRead, MembroAquarioRead, PapelAquario } from '~/types/generated'

const props = defineProps<{
  aquarioId: number
  papel: PapelAquario
}>()

const api = useApi()
const toast = useToast()

const membros = ref<MembroAquarioRead[]>([])
const carregando = ref(true)
const saindo = ref(false)

const convite = ref<ConviteAquarioRead | null>(null)
const gerando = ref(false)
const expiraEm = ref(0)
const agora = useNow({ interval: 1000 })

const segundosRestantes = computed(() => Math.max(0, Math.ceil((expiraEm.value - agora.value.getTime()) / 1000)))

const tempoRestante = computed(() => {
  const minutos = Math.floor(segundosRestantes.value / 60)
  const segundos = segundosRestantes.value % 60
  return `${minutos}:${String(segundos).padStart(2, '0')}`
})

const papeis: Record<PapelAquario, { nome: string, icone: string, cor: 'warning' | 'info' | 'neutral' }> = {
  dono: { nome: 'Dono', icone: 'i-lucide-crown', cor: 'warning' },
  operador: { nome: 'Operador', icone: 'i-lucide-wrench', cor: 'info' },
  leitor: { nome: 'Leitor', icone: 'i-lucide-eye', cor: 'neutral' },
}

function mensagemErro(error: unknown, padrao: string): string {
  if (error instanceof FetchError && typeof error.data?.detail === 'string') {
    return error.data.detail
  }
  return padrao
}

async function carregarMembros() {
  carregando.value = true

  try {
    membros.value = await api(`/aquarios/${props.aquarioId}/membros`)
  }
  catch {
    membros.value = []
  }
  finally {
    carregando.value = false
  }
}

async function gerarConvite() {
  gerando.value = true

  try {
    const inicio = Date.now()
    const resposta: ConviteAquarioRead = await api(`/aquarios/${props.aquarioId}/convites`, { method: 'POST' })

    convite.value = resposta
    expiraEm.value = inicio + resposta.expira_em_segundos * 1000
  }
  catch (error) {
    toast.add({ title: mensagemErro(error, 'Não foi possível gerar o convite'), color: 'error' })
  }
  finally {
    gerando.value = false
  }
}

async function copiarConvite() {
  if (!convite.value || segundosRestantes.value === 0) return

  try {
    await navigator.clipboard.writeText(convite.value.convite)
    toast.add({ title: 'Convite copiado', color: 'success' })
  }
  catch {
    toast.add({ title: 'Selecione o código e copie manualmente', color: 'error' })
  }
}

async function sair() {
  saindo.value = true

  try {
    await api(`/aquarios/${props.aquarioId}/sair`, { method: 'DELETE' })
    toast.add({ title: 'Você saiu do aquário', color: 'success' })
    await navigateTo('/aquarios')
  }
  catch (error) {
    toast.add({ title: mensagemErro(error, 'Não foi possível sair do aquário'), color: 'error' })
  }
  finally {
    saindo.value = false
  }
}

onMounted(carregarMembros)
</script>
