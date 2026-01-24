// Simple i18n implementation for Clouvel landing page
const i18n = {
  currentLang: 'en',
  translations: {},

  async init() {
    // Detect language from URL or localStorage
    const urlParams = new URLSearchParams(window.location.search);
    const urlLang = urlParams.get('lang');
    const storedLang = localStorage.getItem('clouvel-lang');

    this.currentLang = urlLang || storedLang || 'en';

    await this.loadTranslations(this.currentLang);
    this.applyTranslations();
    this.updateLangToggle();
  },

  async loadTranslations(lang) {
    try {
      const response = await fetch(`i18n/${lang}.json`);
      this.translations = await response.json();
    } catch (error) {
      console.error('Failed to load translations:', error);
      // Fallback to English
      if (lang !== 'en') {
        await this.loadTranslations('en');
      }
    }
  },

  get(key) {
    const keys = key.split('.');
    let value = this.translations;
    for (const k of keys) {
      value = value?.[k];
    }
    return value || key;
  },

  applyTranslations() {
    // Update page title
    const title = this.get('meta.title');
    if (title && title !== 'meta.title') {
      document.title = title;
    }

    // Update meta description
    const desc = this.get('meta.description');
    if (desc && desc !== 'meta.description') {
      document.querySelector('meta[name="description"]')?.setAttribute('content', desc);
      document.querySelector('meta[property="og:description"]')?.setAttribute('content', desc);
      document.querySelector('meta[name="twitter:description"]')?.setAttribute('content', desc);
    }

    // Update meta titles
    const ogTitle = this.get('meta.title');
    if (ogTitle && ogTitle !== 'meta.title') {
      document.querySelector('meta[property="og:title"]')?.setAttribute('content', ogTitle);
      document.querySelector('meta[name="twitter:title"]')?.setAttribute('content', ogTitle);
    }

    // Apply to elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const translation = this.get(key);
      if (translation && translation !== key) {
        el.textContent = translation;
      }
    });

    // Apply to elements with data-i18n-placeholder attribute
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      const translation = this.get(key);
      if (translation && translation !== key) {
        el.placeholder = translation;
      }
    });

    // Apply to elements with data-i18n-html attribute (for innerHTML)
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
      const key = el.getAttribute('data-i18n-html');
      const translation = this.get(key);
      if (translation && translation !== key) {
        el.innerHTML = translation;
      }
    });
  },

  updateLangToggle() {
    const toggleBtn = document.getElementById('lang-toggle');
    if (toggleBtn) {
      toggleBtn.textContent = this.currentLang === 'en' ? '한국어' : 'English';
    }
  },

  async switchLang(lang) {
    this.currentLang = lang;
    localStorage.setItem('clouvel-lang', lang);
    await this.loadTranslations(lang);
    this.applyTranslations();
    this.updateLangToggle();

    // Update URL without reload
    const url = new URL(window.location);
    url.searchParams.set('lang', lang);
    window.history.replaceState({}, '', url);
  },

  toggle() {
    const newLang = this.currentLang === 'en' ? 'ko' : 'en';
    this.switchLang(newLang);
  }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  i18n.init();
});

// Expose globally
window.i18n = i18n;
