import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import { siteBase } from './scripts/site-base.mjs';

const base = siteBase();
const site = process.env.PUBLIC_SITE_URL || 'http://localhost:4321';

export default defineConfig({
  site,
  base,
  integrations: [
    starlight({
      title: 'Android Interview Lab',
      description: 'مختبر عملي لمقابلات Senior Android Engineering',
      favicon: '/favicon.svg',
      defaultLocale: 'root',
      locales: {
        root: { label: 'العربية', lang: 'ar-EG', dir: 'rtl' },
      },
      customCss: ['./src/styles/academy.css'],
      head: [
        { tag: 'meta', attrs: { name: 'theme-color', content: '#101827' } },
        { tag: 'script', attrs: { type: 'module', src: `${base}scripts/progress.js` } },
        { tag: 'script', attrs: { type: 'module', src: `${base}scripts/interview-lab.js` } },
      ],
      social: [],
      sidebar: [
        { label: 'لوحة المذاكرة', link: '/' },
        { label: 'Android Interview Lab', link: '/lab/' },
        { label: 'Explore 485 questions', link: '/lab/explore/' },
        { label: 'Review', link: '/lab/review/' },
        { label: 'Practice', link: '/lab/practice/' },
        { label: 'Study plans', link: '/lab/plans/' },
        { label: 'مسار الـ48 يوم', link: '/study-path/' },
        { label: 'الموديولات', link: '/modules/' },
        { label: 'بنك الأسئلة', link: '/question-bank/' },
        { label: 'السيناريوهات', collapsed: true, items: [{ autogenerate: { directory: 'scenarios' } }] },
        { label: 'المعامل والتحديات', collapsed: true, items: [{ autogenerate: { directory: 'labs' } }] },
        { label: 'الدروس المكتملة', collapsed: true, items: [{ autogenerate: { directory: 'lessons' } }] },
        { label: 'المراجعة والفلاش كاردز', collapsed: true, items: [{ autogenerate: { directory: 'revision' } }] },
        { label: 'English Speaking', collapsed: true, items: [{ autogenerate: { directory: 'speaking' } }] },
        { label: 'Glossary', link: '/glossary/' },
        { label: 'Mock Interviews', link: '/mocks/' },
        { label: 'دليل التحقق', link: '/reference/build-verification/' },
      ],
    }),
  ],
});
