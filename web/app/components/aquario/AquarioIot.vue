<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <div class="flex size-10 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-500 ring ring-emerald-500/25 ring-inset">
            <UIcon
              name="i-lucide-cpu"
              class="size-5"
            />
          </div>

          <div>
            <h2 class="font-medium">
              Central IoT
            </h2>
            <p class="text-xs text-muted">
              {{ dispositivo ? 'Lê os sensores e liga o aquecedor' : 'Nenhuma central conectada' }}
            </p>
          </div>
        </div>

        <span
          v-if="dispositivo"
          class="flex items-center gap-1.5 text-sm font-medium"
          :class="online ? 'text-success' : 'text-muted'"
        >
          <span class="relative flex size-2.5">
            <span
              v-if="online"
              class="absolute inline-flex size-full animate-ping rounded-full bg-success opacity-75"
            />
            <span
              class="relative inline-flex size-2.5 rounded-full"
              :class="online ? 'bg-success' : 'bg-neutral-500'"
            />
          </span>
          {{ online ? 'Online' : 'Offline' }}
        </span>
      </div>
    </template>

    <div
      v-if="dispositivo"
      class="space-y-4"
    >
      <dl
        class="grid grid-cols-2 gap-3 text-sm"
        :class="{ 'sm:grid-cols-3': papel === 'dono' }"
      >
        <div class="rounded-lg bg-elevated/50 p-3">
          <dt class="text-xs text-muted">
            Último contato
          </dt>
          <dd class="font-medium">
            {{ haQuanto(dispositivo.ultimo_contato) }}
          </dd>
        </div>

        <div class="rounded-lg bg-elevated/50 p-3">
          <dt class="text-xs text-muted">
            Firmware
          </dt>
          <dd class="font-medium">
            {{ dispositivo.firmware ?? '—' }}
          </dd>
        </div>

        <!-- nome do wifi so o dono ve, o back nem manda pros outros -->
        <div
          v-if="papel === 'dono'"
          class="col-span-2 rounded-lg bg-elevated/50 p-3 sm:col-span-1"
        >
          <dt class="text-xs text-muted">
            Rede Wi-Fi
          </dt>
          <dd class="font-medium wrap-anywhere">
            {{ dispositivo.rede ?? '—' }}
          </dd>
        </div>
      </dl>

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
      :schema="schemaCodigo"
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
          inputmode="numeric"
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
import { z } from 'zod'
import type { CodigoDispositivo, DispositivoRead, PapelAquario } from '~/types/generated'

const props = defineProps<{
  aquarioId: number
  papel: PapelAquario
  dispositivo: DispositivoRead | null
}>()

const emit = defineEmits<{ atualizado: [dispositivo: DispositivoRead | null] }>()

const api = useApi()
const toast = useToast()

const haQuanto = useHaQuanto()
const online = computed(() => props.dispositivo?.estado === 'online')

// vem sem os dois pontos do topico

const formulario = reactive({ codigo: '' })
const schemaCodigo = z.object({ codigo: zCodigoSeisDigitos })
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
