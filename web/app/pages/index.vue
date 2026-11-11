<template>
  <div>
    <h1 class="text-xl font-semibold" style="color: purple">
      Codigo Roxo! Apresentação é sexta!
    </h1>
    <p class="text-muted mt-1">
      pagina
    </p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'role' })
</script>
