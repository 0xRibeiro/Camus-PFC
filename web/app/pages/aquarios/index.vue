<template>
  <div class="mx-auto w-full max-w-6xl space-y-6 px-4 pb-6">
    <UPageHeader
      title="Meus aquários"
      description="Gerencie os aquários vinculados à sua conta."
    >
      <template #links>
        <UButton
          label="Entrar em aquário"
          icon="i-lucide-log-in"
          variant="outline"
          :disabled="carregando || erroCarregamento"
          @click="entrarAberto = true"
        />
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
      class="space-y-8"
    >
      <section
        v-for="grupo in grupos"
        :key="grupo.titulo"
        class="space-y-3"
      >
        <h2 class="text-lg font-semibold">
          {{ grupo.titulo }}
        </h2>

        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <UCard
            v-for="aquario in grupo.aquarios"
            :key="aquario.id"
          >
            <div class="flex items-start justify-between gap-2">
              <h3 class="break-words font-semibold">
                {{ aquario.nome }}
              </h3>
              <UBadge
                :label="aquario.papel ?? 'dono'"
                color="neutral"
                variant="subtle"
              />
            </div>
            <p class="mt-1 text-sm text-muted">
              {{ aquario.litros === null ? 'Volume não informado' : `${aquario.litros} L` }}
            </p>
            <UButton
              :to="`/aquarios/${aquario.id}`"
              label="Abrir aquário"
              icon="i-lucide-arrow-right"
              variant="outline"
              class="mt-4"
            />
          </UCard>
        </div>
      </section>
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

    <UModal
      v-model:open="entrarAberto"
      title="Entrar em aquário"
      :dismissible="!entrando"
    >
      <template #body>
        <div class="space-y-6">
          <UForm
            :schema="zCodigoDispositivo"
            :state="formCodigo"
            class="space-y-3"
            @submit="entrarComCodigo"
          >
            <UFormField
              name="codigo"
              label="Código do IoT"
              description="Gerado na tela Vínculo do aparelho. Entra como operador."
            >
              <UInput
                v-model="formCodigo.codigo"
                placeholder="000000"
                maxlength="6"
                class="w-full sm:w-40"
              />
            </UFormField>

            <UButton
              type="submit"
              label="Entrar com código"
              :loading="entrando"
            />
          </UForm>

          <USeparator />

          <UForm
            :schema="zAquarioEntrar"
            :state="formConvite"
            class="space-y-3"
            @submit="entrarComConvite"
          >
            <UFormField
              name="convite"
              label="Código de convite"
              description="Recebido do dono do aquário. Entra só como leitor."
            >
              <UInput
                v-model="formConvite.convite"
                placeholder="Cole o código recebido"
                class="w-full"
              />
            </UFormField>

            <UButton
              type="submit"
              label="Entrar com convite"
              :loading="entrando"
            />
          </UForm>
        </div>
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import { FetchError } from 'ofetch'
import { z } from 'zod'
import type { AquarioEntrar, AquarioRead, CodigoDispositivo } from '~/types/generated'
import { zAquarioEntrar, zCodigoDispositivo } from '~/types/generated/zod.gen'

definePageMeta({ middleware: 'role' })

type Aquario = AquarioRead

const api = useApi()
const toast = useToast()

const aquarios = ref<Aquario[]>([])
const carregando = ref(true)
const erroCarregamento = ref(false)
const modalAberto = ref(false)
const cadastrando = ref(false)

const entrarAberto = ref(false)
const entrando = ref(false)
const formCodigo = reactive({ codigo: '' })
const formConvite = reactive({ convite: '' })

function mensagemErro(error: unknown, padrao: string): string {
  if (error instanceof FetchError && typeof error.data?.detail === 'string') {
    return error.data.detail
  }
  return padrao
}

async function entrar(caminho: string, body: CodigoDispositivo | AquarioEntrar) {
  if (entrando.value) return

  entrando.value = true

  try {
    const aquario: Aquario = await api(caminho, { method: 'POST', body })

    entrarAberto.value = false
    formCodigo.codigo = ''
    formConvite.convite = ''
    toast.add({ title: `Você entrou em ${aquario.nome}`, color: 'success' })
    await navigateTo(`/aquarios/${aquario.id}`)
  }
  catch (error) {
    toast.add({ title: mensagemErro(error, 'Não foi possível entrar no aquário'), color: 'error' })
  }
  finally {
    entrando.value = false
  }
}

async function entrarComCodigo(evento: FormSubmitEvent<CodigoDispositivo>) {
  await entrar('/aquarios/entrar-com-codigo', evento.data)
}

async function entrarComConvite(evento: FormSubmitEvent<AquarioEntrar>) {
  await entrar('/aquarios/entrar', evento.data)
}

// ---- separação dos cards ----
// cada aquário cai em um grupo pelo papel e por ter IoT, grupo vazio não aparece

const grupos = computed(() => {
  const donoComIot: Aquario[] = []
  const donoSemIot: Aquario[] = []
  const operador: Aquario[] = []
  const leitor: Aquario[] = []

  for (const aquario of aquarios.value) {
    const papel = aquario.papel ?? 'dono'

    if (papel === 'dono' && aquario.dispositivo) donoComIot.push(aquario)
    else if (papel === 'dono') donoSemIot.push(aquario)
    else if (papel === 'operador') operador.push(aquario)
    else leitor.push(aquario)
  }

  const todos = [
    { titulo: 'Meus aquários com IoT', aquarios: donoComIot },
    { titulo: 'Meus aquários sem IoT', aquarios: donoSemIot },
    { titulo: 'Aquários que gerencio', aquarios: operador },
    { titulo: 'Aquários como convidado', aquarios: leitor },
  ]

  const visiveis = []
  for (const grupo of todos) {
    if (grupo.aquarios.length) visiveis.push(grupo)
  }
  return visiveis
})

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
