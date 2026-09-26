<template>
  <div class="max-w-3xl mx-auto px-4 py-10">
    <UButton
      icon="i-lucide-arrow-left"
      label="Voltar"
      color="neutral"
      variant="link"
      class="px-0 mb-6"
      @click="router.back()"
    />

    <h1 class="text-2xl font-bold mb-1">
      Termos de Uso — Camus
    </h1>
    <p class="text-sm text-muted mb-8">
      Última atualização: 25/09/2026
    </p>

    <p class="text-sm leading-relaxed mb-6">
      Estes Termos de Uso estabelecem as regras para utilização da plataforma Camus,
      desenvolvida como Projeto de Conclusão de Curso (PFC).
    </p>

    <h2 class="text-lg font-semibold mt-8 mb-2">
      1. Uso da plataforma
    </h2>
    <p class="text-sm leading-relaxed mb-4">
      O Camus é uma plataforma educacional que permite acessar trilhas, módulos, conteúdos,
      quizzes, grupos e, quando disponível, informações provenientes de dispositivos IoT.
    </p>
    <p class="text-sm leading-relaxed mb-4">
      O usuário deve utilizar a plataforma de acordo com estes Termos e com a legislação vigente.
    </p>

    <h2 class="text-lg font-semibold mt-8 mb-2">
      2. Cadastro e conta
    </h2>
    <p class="text-sm leading-relaxed mb-4">
      O usuário deve fornecer informações verdadeiras e manter seus dados atualizados.
    </p>
    <p class="text-sm leading-relaxed mb-4">
      A conta é de uso pessoal e o usuário é responsável pela proteção de suas credenciais de acesso.
    </p>

    <h2 class="text-lg font-semibold mt-8 mb-2">
      3. Perfis de acesso
    </h2>
    <p class="text-sm leading-relaxed mb-4">
      A plataforma pode possuir diferentes perfis, como aluno, professor, administrador e autor.
    </p>
    <p class="text-sm leading-relaxed mb-4">
      Cada perfil possui permissões específicas. O usuário não deve tentar acessar informações
      ou funcionalidades que não estejam disponíveis para seu perfil.
    </p>

    <h2 class="text-lg font-semibold mt-8 mb-2">
      4. Condutas proibidas
    </h2>
    <p class="text-sm leading-relaxed mb-2">
      Não é permitido:
    </p>
    <ul class="list-disc pl-5 space-y-1 text-sm leading-relaxed mb-4">
      <li>Utilizar a plataforma para atividades ilegais;</li>
      <li>Acessar contas ou dados de outros usuários sem autorização;</li>
      <li>Tentar burlar mecanismos de segurança;</li>
      <li>Prejudicar o funcionamento da plataforma;</li>
      <li>Inserir códigos maliciosos;</li>
      <li>Copiar ou utilizar indevidamente conteúdos protegidos por direitos autorais;</li>
      <li>Utilizar a plataforma para prejudicar outros usuários.</li>
    </ul>

    <h2 class="text-lg font-semibold mt-8 mb-2">
      5. Conteúdos
    </h2>
    <p class="text-sm leading-relaxed mb-4">
      Os conteúdos disponibilizados no Camus destinam-se às finalidades educacionais da plataforma.
    </p>
    <p class="text-sm leading-relaxed mb-4">
      Os direitos autorais dos conteúdos permanecem com seus respectivos titulares.
    </p>
    <p class="text-sm leading-relaxed mb-4">
      Usuários autorizados que adicionarem conteúdos são responsáveis por possuir os direitos
      ou autorizações necessários para sua publicação.
    </p>

    <h2 class="text-lg font-semibold mt-8 mb-2">
      6. Dados e progresso
    </h2>
    <p class="text-sm leading-relaxed mb-4">
      O Camus poderá registrar informações como progresso em trilhas, resultados de quizzes e
      atividades realizadas para disponibilizar seus recursos educacionais.
    </p>
    <p class="text-sm leading-relaxed mb-4">
      Professores e administradores poderão visualizar informações de alunos quando isso fizer
      parte de suas permissões na plataforma.
    </p>
    <p class="text-sm leading-relaxed mb-4">
      O tratamento de dados pessoais é detalhado na
      <ULink to="/politica-de-privacidade" class="text-primary font-medium">Política de Privacidade</ULink>.
    </p>

    <h2 class="text-lg font-semibold mt-8 mb-2">
      7. Dispositivos IoT
    </h2>
    <p class="text-sm leading-relaxed mb-4">
      Quando disponível, a plataforma poderá receber dados de dispositivos e sensores
      utilizados no ambiente monitorado.
    </p>
    <p class="text-sm leading-relaxed mb-4">
      O funcionamento desses recursos pode depender de equipamentos e serviços externos.
    </p>

    <h2 class="text-lg font-semibold mt-8 mb-2">
      8. Disponibilidade
    </h2>
    <p class="text-sm leading-relaxed mb-4">
      O Camus poderá ficar temporariamente indisponível devido a manutenção, atualizações,
      falhas técnicas ou problemas em serviços externos.
    </p>
    <p class="text-sm leading-relaxed mb-4">
      Não é garantido que a plataforma funcionará de forma ininterrupta ou sem erros.
    </p>

    <h2 class="text-lg font-semibold mt-8 mb-2">
      9. Suspensão de acesso
    </h2>
    <p class="text-sm leading-relaxed mb-4">
      O acesso poderá ser suspenso ou encerrado em caso de uso indevido, violação destes Termos,
      problemas de segurança ou determinação legal.
    </p>

    <h2 class="text-lg font-semibold mt-8 mb-2">
      10. Alterações
    </h2>
    <p class="text-sm leading-relaxed mb-4">
      Estes Termos poderão ser atualizados conforme mudanças na plataforma ou na legislação.
    </p>
    <p class="text-sm leading-relaxed mb-4">
      A versão mais recente ficará disponível na plataforma.
    </p>

    <h2 class="text-lg font-semibold mt-8 mb-2">
      11. Contato
    </h2>
    <p class="text-sm leading-relaxed mb-4">
      Dúvidas sobre estes Termos poderão ser encaminhadas ao canal de contato disponibilizado
      pelo projeto.
    </p>

    <p class="text-xs text-muted mt-10 border-t border-default pt-4">
      Este documento faz parte da documentação acadêmica do projeto Camus. Para utilização
      pública ou comercial, recomenda-se revisão jurídica.
    </p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })
const router = useRouter()
</script>