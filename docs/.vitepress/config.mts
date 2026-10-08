import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'torbox-cleaner',
  description: 'Bulk-delete cloud items from your TorBox account.',
  cleanUrls: true,
  head: [
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    [
      'link',
      {
        rel: 'stylesheet',
        href: 'https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Google+Sans+Mono&family=Roboto:wght@400;500&display=swap',
      },
    ],
  ],
  themeConfig: {
    nav: [
      { text: 'Guide', link: '/guide/getting-started' },
      { text: 'CLI reference', link: '/reference/cli' },
      { text: 'TorBox API', link: 'https://api-docs.torbox.app/' },
    ],
    sidebar: [
      {
        text: 'Guide',
        items: [
          { text: 'Getting started', link: '/guide/getting-started' },
          { text: 'Filtering', link: '/guide/filtering' },
          { text: 'Safety', link: '/guide/safety' },
        ],
      },
      {
        text: 'Reference',
        items: [
          { text: 'CLI', link: '/reference/cli' },
          { text: 'API endpoints', link: '/reference/api' },
        ],
      },
    ],
    search: { provider: 'local' },
    outline: { level: [2, 3], label: 'On this page' },
  },
})
