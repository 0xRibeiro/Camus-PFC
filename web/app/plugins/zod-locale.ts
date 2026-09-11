// roda 1x quando o app inicia. deixa as mensagens padrao do zod em pt-br, no app inteiro,
// sem precisar mexer em cada schema individualmente
import { z } from 'zod'
import { ptBR } from 'zod/locales'

export default defineNuxtPlugin(() => {
  z.config(ptBR())
})
