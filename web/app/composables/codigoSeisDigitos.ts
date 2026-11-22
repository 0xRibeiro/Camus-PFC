import { z } from 'zod'

// ------- todo codigo q a pessoa digita no sistema tem 6 numeros: vinculo do iot,
// convite de aquario, convite de grupo e recuperar senha. mesma regra do back (CodigoSeisDigitos)
export const zCodigoSeisDigitos = z
  .string()
  .trim()
  .regex(/^\d{6}$/, 'Digite os 6 números do código')
