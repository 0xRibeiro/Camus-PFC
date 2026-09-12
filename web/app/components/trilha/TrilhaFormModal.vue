<template>
  <!--
    :open="open" @update:open="open = $event" e o "v-model" do UModal por baixo dos panos -
    é exatamente o mesmo mecanismo que a gente usa no nosso proprio componente
    (explico embaixo no script, no defineModel). aqui a gente so repassa pra frente
  -->
  <UModal v-model:open="open" :title="trilha ? 'Editar trilha' : 'Nova trilha'">
    <template #body>
      <UForm :schema="formSchema" :state="formState" class="space-y-4" @submit="onSubmit">
        <UFormField name="titulo" label="Título">
          <UInput v-model="formState.titulo" class="w-full" />
        </UFormField>

        <UFormField name="foto" label="Link da imagem">
          <UInput v-model="formState.foto" placeholder="https://..." class="w-full" />
        </UFormField>

        <!-- preview da imagem, mesmo componente usado no card da listagem -->
        <TrilhaImagem :src="formState.foto" />

        <!-- toggle de ativo so faz sentido editando: trilha nova sempre nasce inativa no back -->
        <UFormField v-if="trilha" name="is_active" label="Trilha ativa">
          <USwitch v-model="formState.is_active" />
        </UFormField>

        <UButton
          type="submit"
          :label="trilha ? 'Salvar' : 'Criar'"
          :loading="saving"
        />
      </UForm>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import type { TrilhaRead } from '~/types/generated'
import { zTrilhaCreate } from '~/types/generated/zod.gen'

// --- v-model:open ---
// quando o pai escreve <TrilhaFormModal v-model:open="showModal" />, o vue "traduz"
// isso, por baixo dos panos, em duas coisas: uma prop chamada "open" (o valor vindo
// de fora) e um evento "update:open" (pra avisar o pai quando o valor deve mudar).
// defineModel('open') e um jeito curto de criar essas duas coisas de uma vez so,
// e ainda devolve uma ref que a gente pode ler E escrever aqui dentro (open.value = false
// fecha o modal, e isso reflete automaticamente na variavel showModal la na pagina)
const open = defineModel<boolean>('open', { required: true })

// esse aqui e uma prop normal (so leitura, vem de fora, n muda sozinha aqui dentro):
// trilha === null significa "modo criar". trilha preenchido significa "modo editar",
// e usamos os dados dela pra pre-encher o formulario (ve o watch mais embaixo)
const props = defineProps<{
  trilha: TrilhaRead | null
  saving: boolean
}>()

// esse componente n sabe chamar a api - ele so valida o formulario e "entrega"
// os dados prontos pro pai, que e quem realmente faz o POST/PATCH
const emit = defineEmits<{
  submit: [dados: { titulo: string, foto?: string | null, is_active: boolean }]
}>()

// --- schema de validacao ---
// zTrilhaCreate e gerado automaticamente a partir do schema TrilhaCreate do back
// (Pydantic, em Python) - toda vez que o back mudar uma regra (tipo minimo de
// caracteres do titulo), esse arquivo gerado atualiza sozinho, sem eu precisar
// reescrever nada aqui. .pick({ titulo: true, foto: true }) pega SO esses 2 campos
// do schema gerado (ele tem mais campos, tipo descricao, que a gente n usa nesse
// formulario) - assim a validacao desses 2 campos continua vindo do back,
// sem eu duplicar a regra (tipo "minimo 3 caracteres") escrevendo ela de novo aqui
const formSchema = zTrilhaCreate.pick({ titulo: true, foto: true })

// esse e o estado real do formulario - o que a pessoa ta digitando agora.
// diferente da prop "trilha" (que so muda quando o pai manda um valor novo),
// isso aqui muda a cada letra digitada
const formState = reactive({ titulo: '', foto: '', is_active: true })

// sempre que a prop "trilha" mudar (o pai abriu o modal pra outra trilha, ou
// pra criar uma nova), a gente reseta o formulario com os dados certos.
// { immediate: true } faz isso rodar tambem na primeira vez que o componente
// aparece, n so quando muda depois
watch(() => props.trilha, (trilha) => {
  if (trilha) {
    formState.titulo = trilha.titulo
    formState.foto = trilha.foto ?? ''
    formState.is_active = trilha.is_active
  }
  else {
    formState.titulo = ''
    formState.foto = ''
    formState.is_active = true
  }
}, { immediate: true })

// o UForm ja validou tudo (bateu com o formSchema) antes de chamar isso -
// aqui a gente so repassa os dados validados pro pai via emit
function onSubmit(event: FormSubmitEvent<{ titulo: string, foto?: string | null }>) {
  emit('submit', {
    titulo: event.data.titulo,
    foto: event.data.foto,
    is_active: formState.is_active,
  })
}
</script>
