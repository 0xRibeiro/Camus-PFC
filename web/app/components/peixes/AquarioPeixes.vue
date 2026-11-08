<template>
  <section class="mt-4 space-y-4 border-t border-default pt-4">
    <UButton
      :label="aberto ? 'Ocultar peixes' : 'Ver peixes'"
      icon="i-lucide-fish"
      color="neutral"
      variant="outline"
      :aria-expanded="aberto"
      @click="alternarPeixes"
    />

    <template v-if="aberto">
      <USkeleton
        v-if="carregando"
        class="h-12 w-full rounded-lg"
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

      <div
        v-else
        class="space-y-4"
      >
        <p
          v-if="!peixes.length"
          class="text-sm text-muted"
        >
          Nenhum peixe cadastrado.
        </p>

        <ul
          v-else
          class="space-y-2"
        >
          <li
            v-for="peixe in peixes"
            :key="peixe.id"
            class="flex items-center gap-3"
          >
            <span aria-hidden="true">🐠</span>
            <div>
              <p class="break-words font-medium">
                {{ peixe.nome }}
              </p>
              <p class="text-sm text-muted">
                {{ peixe.especie }}
              </p>
            </div>
          </li>
        </ul>

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
              :items="zEspecie.options"
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
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import type { PeixeCreate, PeixeRead } from '~/types/generated'
import { zEspecie, zPeixeCreate } from '~/types/generated/zod.gen'

const props = defineProps<{ aquarioId: number }>()

const api = useApi()
const toast = useToast()

const aberto = ref(false)
const carregando = ref(false)
const cadastrando = ref(false)
const peixes = ref<PeixeRead[] | null>(null)

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

async function alternarPeixes() {
  aberto.value = !aberto.value

  if (aberto.value && peixes.value === null && !carregando.value) {
    await carregarPeixes()
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
</script>
