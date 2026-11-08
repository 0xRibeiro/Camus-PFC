<template>
  <section class="space-y-4">
    <USkeleton
      v-if="carregando"
      class="h-52 w-full rounded-xl"
    />

    <div
      v-else-if="peixes === null"
      class="space-y-2"
    >
      <UAlert
        color="error"
        title="Não foi possível carregar os peixes"
      />

      <UButton
        label="Tentar novamente"
        variant="outline"
        @click="carregarPeixes"
      />
    </div>

    <template v-else>
      <div class="flex min-h-52 items-center justify-center rounded-xl border border-sky-500/30 bg-sky-500/10 p-6">
        <p
          v-if="!peixes.length"
          class="text-sm text-muted"
        >
          Seu aquário ainda está vazio.
        </p>

        <ul
          v-else
          class="flex w-full flex-wrap justify-center gap-x-8 gap-y-5"
        >
          <li
            v-for="peixe in peixes"
            :key="peixe.id"
            class="max-w-40 text-center"
          >
            <span
              aria-hidden="true"
              class="block text-3xl"
            >
              {{ emojisPorEspecie[peixe.especie] ?? '🐟' }}
            </span>

            <p class="break-words font-medium">
              {{ peixe.nome }}
            </p>

            <p class="text-xs text-muted">
              {{ peixe.especie }}
            </p>
          </li>
        </ul>
      </div>

      <UForm
        :schema="zPeixeCreate"
        :state="formulario"
        class="space-y-3"
        @submit="cadastrarPeixe"
      >
        <UFormField
          label="Nome do peixe"
          name="nome"
          required
        >
          <UInput
            v-model="formulario.nome"
            placeholder="Ex. Nemo"
            class="w-full"
          />
        </UFormField>

        <UFormField
          label="Espécie"
          name="especie"
          required
        >
          <USelect
            v-model="formulario.especie"
            :items="opcoesEspecie"
            placeholder="Selecione uma espécie"
            class="w-full"
          />
        </UFormField>

        <UButton
          type="submit"
          label="Adicionar peixe"
          :loading="cadastrando"
          :disabled="!formulario.nome.trim() || !formulario.especie"
        />
      </UForm>
    </template>
  </section>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import type { PeixeCreate, PeixeRead } from '~/types/generated'
import { zPeixeCreate } from '~/types/generated/zod.gen'

const props = defineProps<{ aquarioId: number }>()

const api = useApi()
const toast = useToast()

const carregando = ref(true)
const cadastrando = ref(false)
const peixes = ref<PeixeRead[] | null>(null)

const opcoesEspecie = zPeixeCreate.shape.especie.options

const emojisPorEspecie: Partial<Record<PeixeRead['especie'], string>> = {
  'Peixe Dourado': '🎏',
  'Peixe Betta': '🐡',
  'Peixe Palhaço': '🐠',
  'Peixe Anjo': '🦈',
  'Peixe Neon': '🐟',
}

const formulario = reactive({
  nome: '',
  especie: undefined as PeixeCreate['especie'] | undefined,
})

async function carregarPeixes() {
  carregando.value = true

  try {
    peixes.value = await api(`/aquarios/${props.aquarioId}/peixes`)
  }
  catch {
    peixes.value = null
  }
  finally {
    carregando.value = false
  }
}

async function cadastrarPeixe(evento: FormSubmitEvent<PeixeCreate>) {
  if (cadastrando.value || peixes.value === null) return

  cadastrando.value = true

  try {
    const peixe: PeixeRead = await api(`/aquarios/${props.aquarioId}/peixes`, {
      method: 'POST',
      body: {
        nome: evento.data.nome.trim(),
        especie: evento.data.especie,
      },
    })

    peixes.value.push(peixe)
    formulario.nome = ''
    formulario.especie = undefined
    toast.add({ title: 'Peixe cadastrado', color: 'success' })
  }
  catch {
    toast.add({ title: 'Não foi possível cadastrar o peixe', color: 'error' })
  }
  finally {
    cadastrando.value = false
  }
}

onMounted(carregarPeixes)
</script>
