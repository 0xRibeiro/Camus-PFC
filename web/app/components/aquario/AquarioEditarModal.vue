<template>
  <UModal
    v-model:open="open"
    title="Editar aquário"
    :dismissible="!salvando"
  >
    <template #body>
      <UForm
        :schema="schema"
        :state="formulario"
        class="space-y-4"
        @submit="salvar"
      >
        <UFormField
          label="Nome"
          name="nome"
          required
        >
          <UInput
            v-model="formulario.nome"
            class="w-full"
          />
        </UFormField>

        <!-- deixar vazio apaga o volume, igual no cadastro ele e opcional -->
        <UFormField
          label="Volume em litros (opcional)"
          name="litros"
        >
          <UInput
            v-model="formulario.litros"
            type="number"
            min="1"
            step="1"
            class="w-full"
          />
        </UFormField>

        <div class="flex justify-end gap-2">
          <UButton
            label="Cancelar"
            color="neutral"
            variant="outline"
            :disabled="salvando"
            @click="open = false"
          />
          <UButton
            type="submit"
            label="Salvar"
            :loading="salvando"
          />
        </div>
      </UForm>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import { z } from 'zod'
import type { AquarioRead } from '~/types/generated'

const open = defineModel<boolean>('open', { required: true })

const props = defineProps<{
  aquario: AquarioRead
}>()

const emit = defineEmits<{
  salvo: [aquario: AquarioRead]
}>()

const api = useApi()
const toast = useToast()
const salvando = ref(false)

const formulario = reactive({
  nome: '',
  litros: '',
})

// mesmas regras do cadastro
const schema = z.object({
  nome: z.string().trim().min(1, 'Informe o nome').max(50, 'Use até 50 caracteres'),
  litros: z.preprocess(
    valor => valor === '' || valor == null ? undefined : Number(valor),
    z.number({ error: 'Informe um número inteiro positivo' })
      .int('Informe um número inteiro')
      .positive('Informe um volume maior que zero')
      .optional(),
  ),
})

// abre sempre com o que ta salvo agora
watch(open, (aberto) => {
  if (!aberto) return
  formulario.nome = props.aquario.nome
  formulario.litros = props.aquario.litros === null ? '' : String(props.aquario.litros)
})

async function salvar(evento: FormSubmitEvent<z.output<typeof schema>>) {
  salvando.value = true

  try {
    // litros vazio vai como null pro back apagar
    const aquario: AquarioRead = await api(`/aquarios/${props.aquario.id}`, {
      method: 'PATCH',
      body: { nome: evento.data.nome, litros: evento.data.litros ?? null },
    })

    emit('salvo', aquario)
    open.value = false
    toast.add({ title: 'Aquário atualizado', color: 'success' })
  }
  catch {
    toast.add({ title: 'Não foi possível salvar o aquário', color: 'error' })
  }
  finally {
    salvando.value = false
  }
}
</script>
