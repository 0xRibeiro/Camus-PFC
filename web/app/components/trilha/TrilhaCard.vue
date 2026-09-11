<template>
  <UCard>
    <!-- imagem + status + titulo + descricao, tudo dentro do link pra edicao -->
    <NuxtLink :to="`/author/trilhas/${trilha.id}`" class="block">
      <TrilhaImagem :src="trilha.foto" :alt="trilha.titulo" />

      <div class="mt-3 space-y-1">
        <!-- bolinha + texto: verde quando ativa, cinza quando desativada -->
        <div
          class="flex items-center gap-1.5 text-xs font-medium"
          :class="trilha.is_active ? 'text-success' : 'text-dimmed'"
        >
          <span
            class="size-1.5 rounded-full"
            :class="trilha.is_active ? 'bg-success' : 'bg-dimmed'"
          />
          {{ trilha.is_active ? 'ATIVA' : 'DESATIVADA' }}
        </div>

        <p class="font-semibold">
          {{ trilha.titulo }}
        </p>
        <p v-if="trilha.descricao" class="text-sm text-muted line-clamp-2">
          {{ trilha.descricao }}
        </p>
      </div>
    </NuxtLink>

    <!-- rodape do card: contagem de modulo/conteudo + botao editar/excluir -->
    <template #footer>
      <div class="flex items-center justify-between">
        <span class="flex items-center gap-1 text-xs text-muted">
          <UIcon name="i-lucide-layers" class="size-4" />
          {{ modulosCount }} módulo{{ modulosCount === 1 ? '' : 's' }}
          · {{ conteudosCount }} conteúdo{{ conteudosCount === 1 ? '' : 's' }}
        </span>

        <div class="flex items-center gap-1">
          <!--
            botao editar so avisa o pai que o botao foi clicado (emit('edit')).
            esse componente n sabe abrir modal, n sabe chamar api, n sabe nada disso -
            ele so sabe desenhar a trilha na tela e "levantar a mao" quando algo acontece.
            quem decide o que fazer com esse aviso e a pagina (index.vue), que e quem
            realmente controla o modal e fala com o back. isso e o que chamamos de
            "componente burro": ele tem 0 logica de negocio dentro dele.
          -->
          <UButton
            icon="i-lucide-pencil"
            color="neutral"
            variant="ghost"
            size="xs"
            @click="emit('edit')"
          />
          <UButton
            icon="i-lucide-trash"
            color="error"
            variant="ghost"
            size="xs"
            @click="emit('delete')"
          />
        </div>
      </div>
    </template>
  </UCard>
</template>

<script setup lang="ts">
// TrilhaRead e um tipo, n existe de verdade quando o codigo roda - ele so ajuda
// o typescript a saber o formato da trilha (quais campos tem, qual o tipo de cada um).
// vem gerado automaticamente a partir do que o back devolve (ve o types.gen.ts se
// quiser ver o tipo completo) - a gente n escreve esse tipo na mao, ele fica sincronizado
// sozinho com o back sempre que rodamos o comando que gera esses arquivos de novo
import type { TrilhaRead } from '~/types/generated'

// defineProps declara o que esse componente RECEBE de fora (do componente pai).
// e so leitura - esse componente n pode alterar trilha.titulo direto, por exemplo,
// ele so pode ler e mostrar. quem manda o valor de "trilha" e quem usa
// <TrilhaCard :trilha="..." /> - nesse caso, vai ser a pagina index.vue
defineProps<{
  trilha: TrilhaRead
  modulosCount: number
  conteudosCount: number
}>()

// defineEmits declara os "avisos" que esse componente pode mandar pro pai.
// aqui sao dois avisos possiveis: "edit" e "delete", nenhum dos dois carrega
// dado nenhum junto (por isso o [] vazio - se precisasse mandar um valor junto,
// seria tipo emit: [novoValor: boolean], igual fizemos no ModuloItem la atras)
const emit = defineEmits<{
  edit: []
  delete: []
}>()
</script>
