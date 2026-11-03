<template>
  <div class="mx-auto w-full max-w-6xl space-y-6 px-4 pb-6">
    <UPageHeader
      title="Meus aquários"
      description="Gerencie os aquários vinculados à sua conta."
    >
      <template #links>
        <UButton
          label="Cadastrar aquário"
          icon="i-lucide-plus"
          disabled
        />
      </template>
    </UPageHeader>

    <UEmpty
      icon="i-lucide-waves"
      title="Nenhum aquário cadastrado"
      description="Seus aquários aparecerão aqui após o cadastro."
    />
  </div>
</template>
