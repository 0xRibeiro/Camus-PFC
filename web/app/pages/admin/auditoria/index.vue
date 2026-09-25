<template>
  <div>
    <h1 class="text-xl font-semibold mb-4">
      Auditoria
    </h1>

    <AuditoriaTable :logs="logs" :loading="loading" />
  </div>
</template>

<script setup lang="ts">
import type { LogAuditoriaRead } from '~/types/generated'

definePageMeta({ middleware: 'role', roles: ['admin'] })

const logs = ref<LogAuditoriaRead[]>([])
const loading = ref(true)

async function fetchLogs() {
  loading.value = true
  const api = useApi()
  logs.value = await api('/admin/auditoria')
  loading.value = false
}

onMounted(fetchLogs)
</script>
