// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://zonaalcaravaneras.com',
  // /ruta es una página de trabajo interno: fuera del sitemap
  integrations: [sitemap({ filter: (pagina) => !pagina.includes('/ruta') })],
});
