<script setup lang="ts">
import type { JSONContent } from '@tiptap/core'
import { TaskList, TaskItem } from '@tiptap/extension-list'
import { TableKit } from '@tiptap/extension-table'
import { CodeBlockShiki } from 'tiptap-extension-code-block-shiki'
import { EspecieInat } from '~/components/editor/EspecieInatExtension'
import { ImageUpload } from '~/components/editor/ImageUploadExtension'

// mostra o artigo pro aluno, msm editor do author so q sem editar
const props = defineProps<{
  conteudo: JSONContent | null | undefined
}>()

const conteudoLocal = computed(() => props.conteudo ?? undefined)

const { extension: Emoji } = useEditorEmojis()

// precisa das msms extensoes do author senao os blocos n renderizam
const extensions = [
  CodeBlockShiki.configure({
    defaultTheme: 'material-theme',
    themes: {
      light: 'material-theme-lighter',
      dark: 'material-theme-palenight',
    },
  }),
  Emoji,
  EspecieInat,
  ImageUpload,
  TableKit,
  TaskList,
  TaskItem,
]
</script>

<template>
  <UEditor
    :model-value="conteudoLocal"
    content-type="json"
    :extensions="extensions"
    :editable="false"
    :ui="{
      base: 'p-4 sm:px-14',
      content: 'max-w-4xl mx-auto',
    }"
  />
</template>
