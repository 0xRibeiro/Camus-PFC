<template>
  <div class="mx-auto w-full max-w-6xl space-y-6 px-4 pb-6">
    <UPageHeader
      title="Meus aquários"
      description="Gerencie os aquários vinculados à sua conta."
    >
      <template #links>
        <UButton
          label="Cadastrar aquário"
          icon="i-lucide-plus"
          :disabled="carregando || erroCarregamento"
          @click="modalAberto = true"
        />
      </template>
    </UPageHeader>

    <USkeleton
      v-if="carregando"
      class="h-24 w-full rounded-lg"
    />

    <div
      v-else-if="erroCarregamento"
      class="space-y-3"
    >
      <UAlert
        color="error"
        title="Não foi possível carregar os aquários"
      />
      <UButton
        label="Tentar novamente"
        variant="outline"
        @click="carregarAquarios"
      />
    </div>

    <UEmpty
      v-else-if="!aquarios.length"
      icon="i-lucide-waves"
      title="Nenhum aquário cadastrado"
      description="Seus aquários aparecerão aqui após o cadastro."
    />

    <div
      v-else
      class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
    >
      <UCard
        v-for="aquario in aquarios"
        :key="aquario.id"
      >
        <h2 class="break-words font-semibold">
          {{ aquario.nome }}
        </h2>
        <p class="mt-1 text-sm text-muted">
          {{ aquario.litros === null ? 'Volume não informado' : `${aquario.litros} L` }}
        </p>
      </UCard>
    </div>

    <UModal
      v-model:open="modalAberto"
      title="Cadastrar aquário"
      :dismissible="!cadastrando"
    >
      <template #body>
        <UForm
          :schema="schema"
          :state="formulario"
          class="space-y-4"
          @submit="cadastrarAquario"
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

          <UButton
            type="submit"
            label="Cadastrar"
            :loading="cadastrando"
          />
        </UForm>
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import { z } from 'zod'

definePageMeta({ middleware: 'role' })

type Aquario = {
  id: number
  nome: string
  litros: number | null
}

const api = useApi()
const toast = useToast()

const aquarios = ref<Aquario[]>([])
const carregando = ref(true)
const erroCarregamento = ref(false)
const modalAberto = ref(false)
const cadastrando = ref(false)

const formulario = reactive({
  nome: '',
  litros: '',
})

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

async function carregarAquarios() {
  carregando.value = true
  erroCarregamento.value = false

  try {
    aquarios.value = await api('/aquarios')
  }
  catch {
    erroCarregamento.value = true
  }
  finally {
    carregando.value = false
  }
}

async function cadastrarAquario(evento: FormSubmitEvent<z.output<typeof schema>>) {
  if (cadastrando.value) return

  cadastrando.value = true

  try {
    const aquario: Aquario = await api('/aquarios', {
      method: 'POST',
      body: evento.data,
    })

    aquarios.value.push(aquario)
    formulario.nome = ''
    formulario.litros = ''
    modalAberto.value = false
    toast.add({ title: 'Aquário cadastrado', color: 'success' })
  }
  catch {
    toast.add({ title: 'Não foi possível cadastrar o aquário', color: 'error' })
  }
  finally {
    cadastrando.value = false
  }
}

onMounted(carregarAquarios)
</script>
