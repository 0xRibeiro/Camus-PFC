<template>
  <UApp>
    <div class="flex min-h-dvh flex-col">
      <NuxtLayout>
        <div class="flex min-w-0 flex-1 flex-col">
          <main class="flex flex-1 flex-col p-4">
            <NuxtPage />
          </main>

          <CamusFooter class="shrink-0" />
        </div>
      </NuxtLayout>
    </div>
  </UApp>
</template>
