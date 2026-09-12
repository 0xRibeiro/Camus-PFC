import withNuxt from './.nuxt/eslint.config.mjs'

export default withNuxt({
  ignores: ['app/types/generated/**'],
}, {
  rules: {
    '@typescript-eslint/no-explicit-any': 'off',
  },
})
