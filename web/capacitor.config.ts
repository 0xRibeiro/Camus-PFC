import type { CapacitorConfig } from '@capacitor/cli'

// config do app mobile, o webDir é a saida do nuxt generate
const config: CapacitorConfig = {
  appId: 'com.camus.app',
  appName: 'Camus',
  webDir: '.output/public',
}

export default config
