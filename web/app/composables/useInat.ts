export function useInat() {
  const config = useRuntimeConfig()

  return $fetch.create({
    baseURL: config.public.inatBase,
  })
}
