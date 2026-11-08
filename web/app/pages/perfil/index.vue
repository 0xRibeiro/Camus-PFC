<template>
  <div class="mx-auto max-w-3xl space-y-8">
    <UPageHeader
      title="Meu perfil"
      description="Escolha seu avatar, a cor de fundo e seu nome."
    />

    <UCard>
      <div class="flex flex-col items-center gap-6 sm:flex-row">
        <UsuarioAvatar
          :avatar="avatarEscolhido"
          :cor-fundo="cor"
          :tamanho="120"
        />

        <div class="min-w-0 flex-1 space-y-3">
          <UFormField
            label="Nome de usuário"
            :error="erroUsername"
          >
            <UInput
              v-model="username"
              class="w-full"
              maxlength="50"
              @update:model-value="erroUsername = undefined"
            />
          </UFormField>

          <p class="truncate text-sm text-muted">
            {{ auth.user?.email }}
          </p>
          <UBadge
            :label="auth.user?.role"
            variant="subtle"
          />
        </div>

        <!-- seletor de cor do nuxt ui, abre num popover -->
        <UPopover>
          <UButton
            label="Cor de fundo"
            color="neutral"
            variant="outline"
          >
            <template #leading>
              <span
                class="size-3 rounded-full border border-default"
                :style="{ backgroundColor: cor }"
              />
            </template>
          </UButton>

          <template #content>
            <UColorPicker
              v-model="cor"
              class="p-2"
            />
          </template>
        </UPopover>
      </div>
    </UCard>

    <UCard>
      <template #header>
        <p class="font-medium">
          Avatar
        </p>
      </template>

      <div class="grid grid-cols-3 gap-4 sm:grid-cols-6">
        <button
          v-for="chave in avatares"
          :key="chave"
          type="button"
          class="flex justify-center rounded-xl p-2 transition hover:bg-elevated"
          :class="chave === avatarEscolhido ? 'ring-2 ring-primary' : ''"
          :aria-label="chave"
          @click="avatarEscolhido = chave"
        >
          <UsuarioAvatar
            :avatar="chave"
            :cor-fundo="cor"
            :tamanho="64"
          />
        </button>
      </div>
    </UCard>

    <div class="flex justify-end">
      <UButton
        label="Salvar"
        icon="i-lucide-check"
        :loading="salvando"
        :disabled="!mudou || !usernameValido"
        @click="salvar"
      />
    </div>

    <!-- excluir conta (soft delete: os dados pessoais sao anonimizados) -->
    <UCard v-if="auth.role !== 'admin'">
      <div class="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <p class="font-medium text-highlighted">
            Excluir conta
          </p>
          <p class="text-sm text-muted">
            Seus dados pessoais serão anonimizados e você não conseguirá mais entrar.
          </p>
        </div>
        <UButton
          label="Excluir conta"
          icon="i-lucide-trash-2"
          color="error"
          variant="outline"
          @click="confirmando = true"
        />
      </div>
    </UCard>

    <UModal
      v-model:open="confirmando"
      title="Excluir conta"
      description="Essa ação não pode ser desfeita. Seu nome de usuário e e-mail serão removidos e o acesso encerrado."
    >
      <template #footer="{ close }">
        <UButton
          label="Cancelar"
          color="neutral"
          variant="outline"
          @click="close"
        />
        <UButton
          label="Excluir minha conta"
          color="error"
          :loading="excluindo"
          @click="excluirConta"
        />
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
// so exige estar logado, qualquer papel
definePageMeta({ middleware: 'role' })

const auth = useAuthStore()
const toast = useToast()

const avatares = ref<string[]>([])
const avatarEscolhido = ref(auth.user?.avatar ?? 'peixe-palhaco')
const cor = ref(auth.user?.cor_fundo ?? '#0EA5E9')
const username = ref(auth.user?.username ?? '')
const erroUsername = ref<string | undefined>()
const salvando = ref(false)
const confirmando = ref(false)
const excluindo = ref(false)

// mesmo limite do back (3 a 50 caracteres)
const usernameValido = computed(() => username.value.length >= 3 && username.value.length <= 50)

// so habilita o botao se tiver algo diferente do que ta salvo
const mudou = computed(() =>
  avatarEscolhido.value !== auth.user?.avatar
  || cor.value.toUpperCase() !== auth.user?.cor_fundo.toUpperCase()
  || username.value !== auth.user?.username,
)

onMounted(async () => {
  const api = useApi()
  try {
    avatares.value = await api('/avatares')
  }
  catch {
    toast.add({ title: 'Não foi possível carregar os avatares', color: 'error' })
  }
})

async function salvar() {
  const api = useApi()
  salvando.value = true
  erroUsername.value = undefined
  try {
    // o back devolve o usuario ja atualizado, entao troca direto na store
    auth.user = await api('/usuarios/me', {
      method: 'PATCH',
      body: {
        avatar: avatarEscolhido.value,
        cor_fundo: cor.value,
        username: username.value,
      },
    })
    toast.add({ title: 'Perfil atualizado', color: 'success' })
  }
  catch (erro) {
    const e = erro as { status?: number, data?: { detail?: string } }
    if (e.status === 422 && e.data?.detail === 'username já existe') {
      erroUsername.value = 'Esse nome de usuário já está em uso'
    }
    else {
      toast.add({ title: 'Não foi possível salvar', color: 'error' })
    }
  }
  finally {
    salvando.value = false
  }
}

async function excluirConta() {
  const api = useApi()
  excluindo.value = true
  try {
    await api('/usuarios/me', { method: 'DELETE' })
    confirmando.value = false
    // limpa a sessao local e manda pro login
    await auth.logout()
    await navigateTo('/login')
  }
  catch {
    toast.add({ title: 'Não foi possível excluir a conta', color: 'error' })
  }
  finally {
    excluindo.value = false
  }
}
</script>