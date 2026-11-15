<template>
  <UCard>
    <template #header>
      <h2 class="font-medium">
        IoT
      </h2>
    </template>

    <div
      v-if="dispositivo"
      class="space-y-3"
    >
      <div class="flex flex-wrap items-center gap-2">
        <UBadge
          :color="dispositivo.estado === 'online' ? 'success' : 'neutral'"
          :label="dispositivo.estado === 'online' ? 'Online' : 'Offline'"
          variant="subtle"
        />
        <span class="text-sm text-muted">{{ dispositivo.mac }}</span>
      </div>

      <p class="text-sm text-muted">
        Último contato: {{ new Date(dispositivo.ultimo_contato).toLocaleString('pt-BR') }}
      </p>

      <UButton
        v-if="papel === 'dono'"
        label="Desconectar IoT"
        icon="i-lucide-unplug"
        color="error"
        variant="outline"
        @click="confirmarAberto = true"
      />
    </div>

    <UForm
      v-else-if="papel === 'dono'"
      :schema="zCodigoDispositivo"
      :state="formulario"
      class="space-y-3"
      @submit="conectar"
    >
      <p class="text-sm text-muted">
        No aparelho, vá na tela Vínculo, clique em "Gerar código" e digite aqui.
      </p>

      <UFormField
        name="codigo"
        label="Código do IoT"
      >
        <UInput
          v-model="formulario.codigo"
          placeholder="000000"
          maxlength="6"
          class="w-full sm:w-40"
        />
      </UFormField>

      <UButton
        type="submit"
        label="Conectar IoT"
        icon="i-lucide-plug"
        :loading="enviando"
      />
    </UForm>

    <p
      v-else
      class="text-sm text-muted"
    >
      Esse aquário ainda não tem IoT.
    </p>

    <UModal
      v-model:open="confirmarAberto"
      title="Desconectar IoT?"
      description="O IoT sai do aquário e todos os operadores perdem o acesso. Leitores continuam."
      :dismissible="!enviando"
    >
      <template #footer>
        <div class="flex gap-2">
          <UButton
            label="Cancelar"
            color="neutral"
            variant="outline"
            @click="confirmarAberto = false"
          />
          <UButton
            label="Desconectar"
            color="error"
            :loading="enviando"
            @click="desconectar"
          />
        </div>
      </template>
    </UModal>
  </UCard>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import { FetchError } from 'ofetch'
import type { CodigoDispositivo, DispositivoRead, PapelAquario } from '~/types/generated'
import { zCodigoDispositivo } from '~/types/generated/zod.gen'

const props = defineProps<{
  aquarioId: number
  papel: PapelAquario
  dispositivo: DispositivoRead | null
}>()

const emit = defineEmits<{ atualizado: [dispositivo: DispositivoRead | null] }>()

const api = useApi()
const toast = useToast()

const formulario = reactive({ codigo: '' })
const enviando = ref(false)
const confirmarAberto = ref(false)

function mensagemErro(error: unknown, padrao: string): string {
  if (error instanceof FetchError && typeof error.data?.detail === 'string') {
    return error.data.detail
  }
  return padrao
}

async function conectar(evento: FormSubmitEvent<CodigoDispositivo>) {
  enviando.value = true

  try {
    const dispositivo: DispositivoRead = await api(`/aquarios/${props.aquarioId}/dispositivo`, {
      method: 'POST',
      body: evento.data,
    })

    formulario.codigo = ''
    emit('atualizado', dispositivo)
    toast.add({ title: 'IoT conectado', color: 'success' })
  }
  catch (error) {
    toast.add({ title: mensagemErro(error, 'Não foi possível conectar o IoT'), color: 'error' })
  }
  finally {
    enviando.value = false
  }
}

async function desconectar() {
  enviando.value = true

  try {
    await api(`/aquarios/${props.aquarioId}/dispositivo`, { method: 'DELETE' })
    confirmarAberto.value = false
    emit('atualizado', null)
    toast.add({ title: 'IoT desconectado', color: 'success' })
  }
  catch (error) {
    toast.add({ title: mensagemErro(error, 'Não foi possível desconectar o IoT'), color: 'error' })
  }
  finally {
    enviando.value = false
  }
}
</script>
