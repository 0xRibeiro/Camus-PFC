<script setup lang="ts">
import type { EditorCustomHandlers } from '@nuxt/ui'
import type { Editor, JSONContent } from '@tiptap/core'
import { TaskList, TaskItem } from '@tiptap/extension-list'
import { TableKit } from '@tiptap/extension-table'
import { CellSelection } from '@tiptap/pm/tables'
import { CodeBlockShiki } from 'tiptap-extension-code-block-shiki'
import { ImageUpload } from '~/components/editor/ImageUploadExtension'

definePageMeta({ middleware: 'role', roles: ['author', 'admin'] })

const router = useRouter()

function voltarParaTrilha() {
  router.back()
}

const editorRef = useTemplateRef('editorRef')

const customHandlers = {
  imageUpload: {
    canExecute: (editor: Editor) => editor.can().insertContent({ type: 'imageUpload' }),
    execute: (editor: Editor) => editor.chain().focus().insertContent({ type: 'imageUpload' }),
    isActive: (editor: Editor) => editor.isActive('imageUpload'),
    isDisabled: undefined,
  },
  table: {
    canExecute: (editor: Editor) => editor.can().insertTable({ rows: 3, cols: 3, withHeaderRow: true }),
    execute: (editor: Editor) => editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }),
    isActive: (editor: Editor) => editor.isActive('table'),
    isDisabled: undefined,
  },
} satisfies EditorCustomHandlers

const { items: emojiItems, extension: Emoji } = useEditorEmojis()
const { items: suggestionItems } = useEditorSuggestions<typeof customHandlers>()
const { getItems: getDragHandleItems, onNodeChange } = useEditorDragHandle(customHandlers)
const { toolbarItems, bubbleToolbarItems, getImageToolbarItems, getTableToolbarItems } = useEditorToolbar<typeof customHandlers>()

const content = ref<JSONContent>()

const extensions = computed(() => [
  CodeBlockShiki.configure({
    defaultTheme: 'material-theme',
    themes: {
      light: 'material-theme-lighter',
      dark: 'material-theme-palenight',
    },
  }),
  Emoji,
  ImageUpload,
  TableKit,
  TaskList,
  TaskItem,
])
</script>

<template>
  <div>
    <UButton
      icon="i-lucide-arrow-left"
      label="Trilha"
      color="neutral"
      variant="link"
      class="px-0 mb-3"
      @click="voltarParaTrilha"
    />

    <UEditor
      ref="editorRef"
      v-slot="{ editor, handlers }"
      v-model="content"
      content-type="json"
      :extensions="extensions"
      :handlers="customHandlers"
      autofocus
      placeholder="Write, type '/' for commands..."
      :ui="{
        base: 'p-4 sm:px-14',
        content: 'max-w-4xl mx-auto',
      }"
    >
      <div class="sticky top-0 z-10 flex justify-center border-b border-default bg-default py-2">
        <UEditorToolbar
          :editor="editor"
          :items="toolbarItems"
        />
      </div>

      <UEditorToolbar
        :editor="editor"
        :items="bubbleToolbarItems"
        layout="bubble"
        :should-show="({ editor, view, state }: any) => {
          if (editor.isActive('imageUpload') || editor.isActive('image') || state.selection instanceof CellSelection) {
            return false
          }
          const { selection } = state
          return view.hasFocus() && !selection.empty
        }"
      >
        <template #link>
          <EditorLinkPopover :editor="editor" />
        </template>
      </UEditorToolbar>

      <UEditorToolbar
        :editor="editor"
        :items="getImageToolbarItems(editor)"
        layout="bubble"
        :should-show="({ editor, view }: any) => {
          return editor.isActive('image') && view.hasFocus()
        }"
      />

      <UEditorToolbar
        :editor="editor"
        :items="getTableToolbarItems(editor)"
        layout="bubble"
        :should-show="({ editor, view }: any) => {
          return editor.state.selection instanceof CellSelection && view.hasFocus()
        }"
      />

      <UEditorEmojiMenu
        :editor="editor"
        :items="emojiItems"
      />

      <UEditorSuggestionMenu
        :editor="editor"
        :items="suggestionItems"
      />

      <UEditorDragHandle
        v-slot="{ ui, onClick }"
        :editor="editor"
        @node-change="onNodeChange"
      >
        <UButton
          icon="i-lucide-plus"
          color="neutral"
          variant="ghost"
          size="sm"
          :class="ui.handle()"
          @click="(e: MouseEvent) => {
            e.stopPropagation()
            const node = onClick()

            handlers.suggestion?.execute(editor, { pos: node?.pos }).run()
          }"
        />

        <UDropdownMenu
          v-slot="{ open }"
          :modal="false"
          :items="getDragHandleItems(editor)"
          :content="{ side: 'left' }"
          :ui="{ content: 'w-48', label: 'text-xs' }"
          @update:open="editor.chain().setMeta('lockDragHandle', $event).run()"
        >
          <UButton
            color="neutral"
            variant="ghost"
            active-variant="soft"
            size="sm"
            icon="i-lucide-grip-vertical"
            :active="open"
            :class="ui.handle()"
          />
        </UDropdownMenu>
      </UEditorDragHandle>
    </UEditor>
  </div>
</template>
