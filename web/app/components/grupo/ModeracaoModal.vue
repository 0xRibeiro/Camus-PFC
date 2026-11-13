<template>
  <UModal
    v-model:open="open"
    :title="titulo"
    :description="descricao"
  >
    <template #body>
      <UForm
        :schema="formSchema"
        :state="formState"
        class="space-y-4"
        @submit="enviar"
      >
        <UFormField
          v-if="acao === 'suspender'"
          name="dias"
          label="Prazo da suspensão"
          required
        >
          <USelect
            v-model="formState.dias"
            :items="prazos"
            class="w-full"
          />
        </UFormField>

        <UFormField
          name="motivo"
          label="Motivo"
          required
          :hint="`${formState.motivo.length}/500`"
        >
          <UTextarea
            v-model="formState.motivo"
            :maxlength="500"
            :rows="4"
            placeholder="O dono do grupo vai ler esse motivo no aviso"
            class="w-full"
          />
        </UFormField>

        <div class="flex justify-end gap-2">
          <UButton
            label="Cancelar"
            color="neutral"
            variant="outline"
            @click="open = false"
          />
          <UButton
            type="submit"
            :label="rotuloBotao"
            color="error"
            :loading="enviando"
          />
        </div>
      </UForm>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import { FetchError } from 'ofetch'
import { zMotivoCreate, zSuspensaoCreate } from '~/types/generated/zod.gen'

export type AcaoModeracao = 'suspender' | 'excluir_grupo' | 'excluir_conteudo'

// quem abre e fecha o modal é a página que usa ele, como no DenunciaModal
const open = defineModel<boolean>('open', { required: true })

// nomeAlvo vai na descrição: é o nome do grupo ou o título do conteúdo
const props = defineProps<{
  acao: AcaoModeracao
  grupoId: number
  conteudoId?: number | null
  nomeAlvo: string
}>()

const emit = defineEmits<{
  concluida: []
}>()

const api = useApi()
const toast = useToast()

const prazos = [
  { label: '14 dias', value: 14 },
  { label: '30 dias', value: 30 },
]

const titulo = computed(() => {
  if (props.acao === 'suspender') return 'Suspender grupo'
  if (props.acao === 'excluir_grupo') return 'Excluir grupo'
  return 'Apagar conteúdo'
})

const descricao = computed(() => {
  if (props.acao === 'suspender') {
    return `"${props.nomeAlvo}" fica bloqueado: os membros perdem o acesso e o dono só consegue visualizar.`
  }
  if (props.acao === 'excluir_grupo') {
    return `"${props.nomeAlvo}" será excluído com as trilhas, as participações e as denúncias. Isso não pode ser desfeito.`
  }
  return `"${props.nomeAlvo}" será removido do grupo. Isso não pode ser desfeito.`
})

const rotuloBotao = computed(() => {
  if (props.acao === 'suspender') return 'Suspender'
  if (props.acao === 'excluir_grupo') return 'Excluir grupo'
  return 'Apagar conteúdo'
})

// as regras de validação vêm do schema que o back gerou
const formSchema = computed(() => (props.acao === 'suspender' ? zSuspensaoCreate : zMotivoCreate))

const formState = reactive({
  dias: 14 as 14 | 30,
  motivo: '',
})
const enviando = ref(false)

// zera os campos sempre que o modal abre
watch(open, (aberto) => {
  if (!aberto) return
  formState.dias = 14
  formState.motivo = ''
})

function mensagemErro(error: unknown): string {
  if (error instanceof FetchError && typeof error.data?.detail === 'string') {
    return error.data.detail
  }
  return 'Não foi possível concluir a ação'
}

async function executar(motivo: string) {
  if (props.acao === 'suspender') {
    await api(`/admin/grupos/${props.grupoId}/suspensao`, { method: 'POST', body: { dias: formState.dias, motivo } })
  }
  else if (props.acao === 'excluir_grupo') {
    await api(`/admin/grupos/${props.grupoId}`, { method: 'DELETE', body: { motivo } })
  }
  else {
    await api(`/admin/grupos/${props.grupoId}/conteudos/${props.conteudoId}`, { method: 'DELETE', body: { motivo } })
  }
}

async function enviar(event: FormSubmitEvent<{ motivo: string }>) {
  enviando.value = true

  try {
    await executar(event.data.motivo)

    toast.add({ title: 'Ação concluída', description: 'O dono do grupo foi avisado.', color: 'success' })
    open.value = false
    emit('concluida')
  }
  catch (error) {
    toast.add({ title: mensagemErro(error), color: 'error' })
  }
  finally {
    enviando.value = false
  }
}
</script>