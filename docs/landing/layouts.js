/**
 * Clouvel Landing Page - Layout Templates
 * 상황별 레이아웃 동적 전환
 */

const LAYOUTS = {
  // Default: 현재 레이아웃 유지
  default: null,

  // Developer: 터미널 스타일
  developer: {
    hero: `
      <section class="hero-developer pt-32 pb-16 px-6 relative">
        <div class="max-w-4xl mx-auto text-center relative z-10">
          <div class="hero-eyebrow mb-4">THE INTELLIGENT PRD GATE</div>
          <h1 class="hero-title-developer text-4xl md:text-6xl font-bold mb-6">
            PRD 없으면,<br/>
            <span class="typing-container">
              <span class="typing-text">코딩 없다.</span>
            </span>
          </h1>
          <p class="text-lg text-slate-400 mb-8 max-w-xl mx-auto">
            AI가 요구사항을 멋대로 압축하는 순간, PRD-First 게이트로 막는다.
          </p>
          <div class="flex flex-wrap gap-4 justify-center mb-12">
            <a href="#getting-started" class="btn-primary-developer">
              Download
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
              </svg>
            </a>
            <a href="docs.html" class="btn-secondary px-6 py-3 border border-white/20 rounded-lg hover:bg-white/5 transition">
              View Docs
            </a>
          </div>
          <div class="terminal-window">
            <div class="terminal-header">
              <div class="terminal-dot red"></div>
              <div class="terminal-dot yellow"></div>
              <div class="terminal-dot green"></div>
              <span class="ml-4 text-slate-500 text-xs">terminal</span>
            </div>
            <div class="terminal-body">
              <p><span class="terminal-prompt">$</span> <span class="terminal-command">claude "로그인 만들어줘"</span></p>
              <p class="terminal-error mt-2">BLOCK: 코딩 금지</p>
              <p class="terminal-output">PRD 없음 → 문서 먼저 작성하세요</p>
              <p class="mt-4"><span class="terminal-prompt">$</span> <span class="terminal-command">clouvel start</span></p>
              <p class="terminal-success mt-2">✓ PRD 템플릿 생성 완료</p>
            </div>
          </div>
        </div>
      </section>
      <section class="stats-developer max-w-4xl mx-auto px-6">
        <div class="stat">
          <div class="stat-value">50%</div>
          <div class="stat-label">디버깅 시간 절약</div>
        </div>
        <div class="stat">
          <div class="stat-value">100%</div>
          <div class="stat-label">요구사항 추적</div>
        </div>
        <div class="stat">
          <div class="stat-value">0</div>
          <div class="stat-label">누락된 기능</div>
        </div>
      </section>
    `,
  },

  // Premium: Linear 스타일
  premium: {
    hero: `
      <section class="hero-premium pt-40 pb-20 px-6 relative overflow-hidden">
        <div class="ambient-glow top-0 left-1/2 -translate-x-1/2"></div>
        <div class="max-w-4xl mx-auto text-center relative z-10">
          <div class="badge-premium mb-8">
            <span class="w-2 h-2 bg-white rounded-full animate-pulse"></span>
            MCP Server for Claude Code
          </div>
          <h1 class="hero-title-premium text-5xl md:text-7xl font-bold mb-6">
            PRD 없으면,<br/>
            <span class="gradient-text">코딩 없다.</span>
          </h1>
          <p class="hero-subtitle-premium text-xl text-slate-400 mb-10 max-w-2xl mx-auto">
            AI가 요구사항을 멋대로 압축하는 순간,<br/>
            PRD-First 게이트로 막는다.
          </p>
          <div class="flex flex-wrap gap-4 justify-center">
            <a href="#getting-started" class="btn-primary-premium">
              Get started
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
            </a>
            <a href="#demo" class="btn-secondary-premium">
              See demo
            </a>
          </div>
        </div>
      </section>
    `,
  },

  // Minimal: Vercel/xmcp 스타일
  minimal: {
    hero: `
      <section class="hero-minimal min-h-screen flex flex-col justify-center items-center px-6">
        <h1 class="hero-title-minimal text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight mb-4">
          PRD 없으면,<br/>코딩 없다.
        </h1>
        <p class="hero-subtitle-minimal text-lg text-slate-500 mb-8">
          문서 기반 AI 코딩의 새로운 기준
        </p>
        <div class="install-command">
          <code>pip install clouvel</code>
          <button class="copy-btn" onclick="navigator.clipboard.writeText('pip install clouvel')">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
            </svg>
          </button>
        </div>
        <div class="scroll-indicator">↓</div>
      </section>
    `,
  },

  // Friendly: Raycast/Arc 스타일
  friendly: {
    hero: `
      <section class="hero-friendly pt-28 pb-12 px-6">
        <div class="max-w-4xl mx-auto text-center">
          <h1 class="hero-title-friendly text-4xl md:text-5xl font-bold mb-4">
            PRD 없으면, 코딩 없다.
          </h1>
          <p class="hero-subtitle-friendly text-lg text-slate-600 mb-6">
            AI 코딩의 새로운 기준. 문서 먼저, 코딩 나중.
          </p>
          <div class="install-box mb-8">
            <code>pip install clouvel</code>
            <button class="copy-btn" onclick="navigator.clipboard.writeText('pip install clouvel')">Copy</button>
          </div>
          <div class="product-screenshot mb-8">
            <div class="bg-slate-100 rounded-2xl p-8 text-center text-slate-400">
              <svg class="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
              Product Screenshot
            </div>
          </div>
        </div>
      </section>
      <section class="works-with py-4">
        <span class="works-with-label">Works with:</span>
        <span class="works-with-item">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
          CLI
        </span>
        <span class="works-with-item">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M20 3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/></svg>
          Desktop
        </span>
        <span class="works-with-item">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M23.15 2.587L18.21.21a1.494 1.494 0 0 0-1.705.29l-9.46 8.63-4.12-3.128a.999.999 0 0 0-1.276.057L.327 7.261A1 1 0 0 0 .326 8.74L3.899 12 .326 15.26a1 1 0 0 0 .001 1.479L1.65 17.94a.999.999 0 0 0 1.276.057l4.12-3.128 9.46 8.63a1.492 1.492 0 0 0 1.704.29l4.942-2.377A1.5 1.5 0 0 0 24 20.06V3.939a1.5 1.5 0 0 0-.85-1.352z"/></svg>
          VS Code
        </span>
      </section>
    `,
  },

  // Creative: Cloudflare 스타일
  creative: {
    hero: `
      <section class="hero-creative min-h-screen grid md:grid-cols-2 gap-8 items-center px-6 py-20 max-w-6xl mx-auto">
        <div class="hero-illustration order-2 md:order-1">
          <div class="illustration-placeholder"></div>
        </div>
        <div class="hero-content-creative order-1 md:order-2">
          <h1 class="hero-title-creative text-4xl md:text-5xl lg:text-6xl font-extrabold mb-6">
            PRD 없으면,<br/>
            <span class="accent">코딩 없다.</span>
          </h1>
          <p class="hero-subtitle-creative text-xl text-slate-400 mb-8">
            AI가 멋대로 하는 걸 막는 유일한 방법.<br/>
            문서 기반 개발, 지금 시작하세요.
          </p>
          <div class="flex flex-wrap gap-4">
            <a href="#getting-started" class="btn-creative">
              Start Free
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
              </svg>
            </a>
            <a href="docs.html" class="btn-creative-outline">
              Documentation
            </a>
          </div>
        </div>
      </section>
    `,
  },
};

class LayoutManager {
  constructor() {
    this.currentLayout = "default";
    this.originalContent = {};
    this.initialized = false;
  }

  init() {
    if (this.initialized) return;
    // Save original content
    this.saveOriginalContent();
    this.initialized = true;
  }

  saveOriginalContent() {
    // Save hero section
    const heroSection = document.querySelector("section.pt-32.pb-12");
    if (heroSection) {
      this.originalContent.hero = heroSection.outerHTML;
    }

    // Save works-with section
    const worksWithSection = document.querySelector(
      "section.py-8.px-6.border-t",
    );
    if (worksWithSection) {
      this.originalContent.worksWith = worksWithSection.outerHTML;
    }
  }

  applyLayout(layoutName) {
    this.init();

    const layout = LAYOUTS[layoutName];

    // If default or no layout defined, restore original
    if (!layout) {
      this.restoreOriginal();
      this.currentLayout = "default";
      return;
    }

    // Apply hero layout
    if (layout.hero) {
      const heroSection = document.querySelector(
        "section.pt-32.pb-12, section.hero-developer, section.hero-premium, section.hero-minimal, section.hero-friendly, section.hero-creative",
      );
      const worksWithSection = document.querySelector(
        "section.py-8.px-6.border-t, section.works-with, section.stats-developer",
      );

      if (heroSection) {
        // Create temp container
        const temp = document.createElement("div");
        temp.innerHTML = layout.hero;

        // Replace hero
        heroSection.replaceWith(temp.firstElementChild);

        // Handle additional sections (stats, works-with)
        if (temp.children.length > 1 && worksWithSection) {
          worksWithSection.replaceWith(temp.children[0]);
        } else if (worksWithSection && layoutName === "minimal") {
          // Minimal: hide works-with
          worksWithSection.style.display = "none";
        }
      }
    }

    this.currentLayout = layoutName;

    // Re-init typing animation for developer theme
    if (layoutName === "developer") {
      this.initTypingAnimation();
    }
  }

  restoreOriginal() {
    if (this.originalContent.hero) {
      const currentHero = document.querySelector(
        "section.pt-32.pb-12, section.hero-developer, section.hero-premium, section.hero-minimal, section.hero-friendly, section.hero-creative",
      );
      if (currentHero) {
        const temp = document.createElement("div");
        temp.innerHTML = this.originalContent.hero;
        currentHero.replaceWith(temp.firstElementChild);
      }
    }

    if (this.originalContent.worksWith) {
      const currentWorksWith = document.querySelector(
        "section.py-8.px-6.border-t, section.works-with, section.stats-developer",
      );
      if (currentWorksWith) {
        const temp = document.createElement("div");
        temp.innerHTML = this.originalContent.worksWith;
        currentWorksWith.replaceWith(temp.firstElementChild);
      } else {
        // Re-show if hidden
        const hidden = document.querySelector(
          'section[style*="display: none"]',
        );
        if (hidden) hidden.style.display = "";
      }
    }
  }

  initTypingAnimation() {
    const typingText = document.querySelector(".typing-text");
    if (!typingText) return;

    const text = "코딩 없다.";
    let index = 0;
    typingText.textContent = "";

    const type = () => {
      if (index < text.length) {
        typingText.textContent += text.charAt(index);
        index++;
        setTimeout(type, 150);
      }
    };

    setTimeout(type, 500);
  }
}

// Global instance
window.layoutManager = new LayoutManager();
window.LAYOUTS = LAYOUTS;
