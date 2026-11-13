<template>
  <UModal
    v-model:open="open"
    :title="titulo"
    description="A denúncia é enviada para a administração da plataforma, que vai analisar o caso."
  >
    <template #body>
      <UForm
        :schema="formSchema"
        :state="formState"
        class="space-y-4"
        @submit="enviar"
      >
        <UFormField
          name="motivo"
          label="Motivo"
          required
        >
          <USelect
            v-model="formState.motivo"
            :items="motivos"
            placeholder="Selecione um motivo"
            class="w-full"
          />
        </UFormField>

        <UFormField
          name="descricao"
          label="Detalhes (opcional)"
          :hint="`${formState.descricao.length}/500`"
        >
          <UTextarea
            v-model="formState.descricao"
            :maxlength="500"
            :rows="4"
            placeholder="Conte o que aconteceu"
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
            label="Enviar denúncia"
            color="error"
            :loading="enviando"
            :disabled="!formState.motivo"
          />
        </div>
      </UForm>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import { FetchError } from 'ofetch'
import type { DenunciaCreate } from '~/types/generated'
import { zDenunciaCreate } from '~/types/generated/zod.gen'

// mesmo esquema do TrilhaFormModal: quem abre e fecha o modal é a página que usa ele
const open = defineModel<boolean>('open', { required: true })

// sem idConteudo, a denúncia vai contra o grupo; com ele, aponta pra um conteúdo específico
const props = defineProps<{
  grupoId: number
  idConteudo?: number | null
}>()

const emit = defineEmits<{
  enviada: []
}>()

const api = useApi()
const toast = useToast()

const titulo = computed(() => (props.idConteudo ? 'Denunciar conteúdo' : 'Denunciar grupo'))

const motivos = [
  { label: 'Conteúdo impróprio', value: 'conteudo_improprio' },
  { label: 'Assédio', value: 'assedio' },
  { label: 'Spam', value: 'spam' },
  { label: 'Outro', value: 'outro' },
]

// as regras de validação já vêm do schema que o back gerou (zDenunciaCreate)
const formSchema = zDenunciaCreate.pick({ motivo: true, descricao: true })

const formState = reactive({
  motivo: undefined as DenunciaCreate['motivo'] | undefined,
  descricao: '',
})
const enviando = ref(false)

// zera os campos sempre que o modal é aberto
watch(open, (aberto) => {
  if (!aberto) return
  formState.motivo = undefined
  formState.descricao = ''
})

function mensagemErro(error: unknown): string {
  if (error instanceof FetchError && typeof error.data?.detail === 'string') {
    return error.data.detail
  }
  return 'Não foi possível enviar a denúncia'
}

async function enviar(event: FormSubmitEvent<{ motivo: DenunciaCreate['motivo'], descricao?: string | null }>) {
  enviando.value = true

  try {
    const corpo: DenunciaCreate = {
      motivo: event.data.motivo,
      descricao: event.data.descricao || null,
      id_conteudo: props.idConteudo ?? null,
    }

    await api(`/grupos/${props.grupoId}/denuncias`, { method: 'POST', body: corpo })

    toast.add({ title: 'Denúncia enviada', description: 'A administração vai analisar o caso.', color: 'success' })
    open.value = false
    emit('enviada')
  }
  catch (error) {
    toast.add({ title: mensagemErro(error), color: 'error' })
  }
  finally {
    enviando.value = false
  }
}
</script>
