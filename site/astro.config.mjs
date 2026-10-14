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
      description: 'Hands-on Senior Android Engineering Interview Preparation & Question Bank',
      favicon: '/favicon.svg',
      defaultLocale: 'root',
      locales: {
        root: { label: 'English', lang: 'en', dir: 'ltr' },
        ar: { label: 'العربية', lang: 'ar-EG', dir: 'rtl' },
      },
      customCss: ['./src/styles/academy.css'],
      head: [
        { tag: 'meta', attrs: { name: 'theme-color', content: '#101827' } },
        { tag: 'script', attrs: { type: 'module', src: `${base}scripts/progress.js` } },
        { tag: 'script', attrs: { type: 'module', src: `${base}scripts/interview-lab.js` } },
      ],
      social: [],
      sidebar: [
        {
          label: 'Study Dashboard',
          translations: { 'ar': 'لوحة المذاكرة', 'ar-EG': 'لوحة المذاكرة' },
          link: '/',
        },
        {
          label: 'Android Interview Lab',
          translations: { 'ar': 'مختبر أسئلة أندرويد', 'ar-EG': 'مختبر أسئلة أندرويد' },
          link: '/lab/',
        },
        {
          label: 'Explore 485 Questions',
          translations: { 'ar': 'استكشف 485 سؤال', 'ar-EG': 'استكشف 485 سؤال' },
          link: '/lab/explore/',
        },
        {
          label: 'Spaced Review',
          translations: { 'ar': 'المراجعة المتباعدة', 'ar-EG': 'المراجعة المتباعدة' },
          link: '/lab/review/',
        },
        {
          label: 'Mock Practice',
          translations: { 'ar': 'جلسات المحاكاة', 'ar-EG': 'جلسات المحاكاة' },
          link: '/lab/practice/',
        },
        {
          label: 'Study Plans',
          translations: { 'ar': 'خطط المذاكرة', 'ar-EG': 'خطط المذاكرة' },
          link: '/lab/plans/',
        },
        {
          label: '48-Day Path',
          translations: { 'ar': 'مسار الـ48 يوم', 'ar-EG': 'مسار الـ48 يوم' },
          link: '/study-path/',
        },
        {
          label: 'Modules',
          translations: { 'ar': 'الموديولات', 'ar-EG': 'الموديولات' },
          link: '/modules/',
        },
        {
          label: 'Question Bank',
          translations: { 'ar': 'بنك الأسئلة', 'ar-EG': 'بنك الأسئلة' },
          link: '/question-bank/',
        },
        {
          label: 'Scenarios',
          translations: { 'ar': 'السيناريوهات', 'ar-EG': 'السيناريوهات' },
          collapsed: true,
          items: [{ autogenerate: { directory: 'scenarios' } }],
        },
        {
          label: 'Labs & Challenges',
          translations: { 'ar': 'المعامل والتحديات', 'ar-EG': 'المعامل والتحديات' },
          collapsed: true,
          items: [{ autogenerate: { directory: 'labs' } }],
        },
        {
          label: 'Completed Lessons',
          translations: { 'ar': 'الدروس المكتملة', 'ar-EG': 'الدروس المكتملة' },
          collapsed: true,
          items: [{ autogenerate: { directory: 'lessons' } }],
        },
        {
          label: 'Revision & Flashcards',
          translations: { 'ar': 'المراجعة والفلاش كاردز', 'ar-EG': 'المراجعة والفلاش كاردز' },
          collapsed: true,
          items: [{ autogenerate: { directory: 'revision' } }],
        },
        {
          label: 'English Speaking',
          translations: { 'ar': 'التحدث بالإنجليزية', 'ar-EG': 'التحدث بالإنجليزية' },
          collapsed: true,
          items: [{ autogenerate: { directory: 'speaking' } }],
        },
        {
          label: 'Glossary',
          translations: { 'ar': 'قاموس المصطلحات', 'ar-EG': 'قاموس المصطلحات' },
          link: '/glossary/',
        },
        {
          label: 'Mock Interviews',
          translations: { 'ar': 'المقابلات التجريبية', 'ar-EG': 'المقابلات التجريبية' },
          link: '/mocks/',
        },
        {
          label: 'Verification Guide',
          translations: { 'ar': 'دليل التحقق', 'ar-EG': 'دليل التحقق' },
          link: '/reference/build-verification/',
        },
      ],
    }),
  ],
});
