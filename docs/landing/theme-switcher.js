/**
 * Clouvel Landing Page Theme Switcher
 *
 * Available themes:
 * - default:   기본 (Option 10: Hybrid) - 현재 + 개선, 안정적
 * - developer: 개발자 타겟 (Option 4: Warp) - 터미널/AI 코딩 느낌
 * - premium:   프리미엄 느낌 (Option 1: Linear) - 다크 + 프로페셔널
 * - minimal:   미니멀 강조 (Option 3/9: Vercel/xmcp) - 극 미니멀
 * - friendly:  일반 사용자 (Option 2/7: Raycast/Arc) - 친근, 깔끔
 * - creative:  차별화 (Option 5: Cloudflare) - 오렌지 + 크리에이티브
 */

const THEMES = {
  default: {
    name: "Default",
    description: "현재 + 개선, 안정적",
    file: "themes/default.css",
    darkMode: true,
  },
  developer: {
    name: "Developer",
    description: "터미널/AI 코딩 느낌",
    file: "themes/developer.css",
    darkMode: false, // Always dark
  },
  premium: {
    name: "Premium",
    description: "다크 + 프로페셔널",
    file: "themes/premium.css",
    darkMode: false, // Always dark
  },
  minimal: {
    name: "Minimal",
    description: "극 미니멀",
    file: "themes/minimal.css",
    darkMode: true,
  },
  friendly: {
    name: "Friendly",
    description: "친근, 깔끔",
    file: "themes/friendly.css",
    darkMode: true,
  },
  creative: {
    name: "Creative",
    description: "오렌지 + 크리에이티브",
    file: "themes/creative.css",
    darkMode: false, // Always dark
  },
};

class ThemeSwitcher {
  constructor() {
    this.currentTheme = this.getSavedTheme() || "default";
    this.currentMode = this.getSavedMode() || "light";
    this.themeStylesheet = null;
    this.init();
  }

  init() {
    // Create theme stylesheet link
    this.themeStylesheet = document.createElement("link");
    this.themeStylesheet.rel = "stylesheet";
    this.themeStylesheet.id = "theme-stylesheet";
    document.head.appendChild(this.themeStylesheet);

    // Apply saved theme
    this.applyTheme(this.currentTheme);

    // Apply saved dark mode
    if (this.currentMode === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
    }

    // Create theme switcher UI if container exists
    const container = document.getElementById("theme-switcher-container");
    if (container) {
      this.createUI(container);
    }
  }

  createUI(container) {
    const wrapper = document.createElement("div");
    wrapper.className = "theme-switcher";
    wrapper.innerHTML = `
      <div class="theme-switcher-toggle" id="theme-toggle-btn">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"/>
          <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
        </svg>
      </div>
      <div class="theme-switcher-dropdown" id="theme-dropdown">
        <div class="theme-dropdown-header">
          <span>Theme</span>
          <button class="dark-mode-toggle" id="dark-mode-btn" title="Toggle dark mode">
            <svg class="sun-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="5"/>
              <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
            </svg>
            <svg class="moon-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          </button>
        </div>
        <div class="theme-options">
          ${Object.entries(THEMES)
            .map(
              ([key, theme]) => `
            <button class="theme-option ${key === this.currentTheme ? "active" : ""}" data-theme="${key}">
              <span class="theme-name">${theme.name}</span>
              <span class="theme-desc">${theme.description}</span>
            </button>
          `,
            )
            .join("")}
        </div>
      </div>
    `;

    container.appendChild(wrapper);

    // Add event listeners
    const toggleBtn = document.getElementById("theme-toggle-btn");
    const dropdown = document.getElementById("theme-dropdown");
    const darkModeBtn = document.getElementById("dark-mode-btn");

    toggleBtn.addEventListener("click", () => {
      dropdown.classList.toggle("open");
    });

    document.addEventListener("click", (e) => {
      if (!wrapper.contains(e.target)) {
        dropdown.classList.remove("open");
      }
    });

    wrapper.querySelectorAll(".theme-option").forEach((btn) => {
      btn.addEventListener("click", () => {
        const theme = btn.dataset.theme;
        this.applyTheme(theme);
        this.saveTheme(theme);

        // Update active state
        wrapper
          .querySelectorAll(".theme-option")
          .forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");

        dropdown.classList.remove("open");
      });
    });

    darkModeBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      this.toggleDarkMode();
    });

    // Add styles for the switcher
    this.addSwitcherStyles();
  }

  applyTheme(themeName) {
    const theme = THEMES[themeName];
    if (!theme) return;

    this.currentTheme = themeName;
    this.themeStylesheet.href = theme.file;

    // Apply layout if layoutManager exists
    if (window.layoutManager) {
      window.layoutManager.applyLayout(themeName);
    }

    // Handle dark mode availability
    const darkModeBtn = document.getElementById("dark-mode-btn");
    if (darkModeBtn) {
      if (theme.darkMode) {
        darkModeBtn.style.display = "flex";
      } else {
        darkModeBtn.style.display = "none";
        // Force light mode for themes without dark mode toggle
        document.documentElement.removeAttribute("data-theme");
      }
    }
  }

  toggleDarkMode() {
    const isDark =
      document.documentElement.getAttribute("data-theme") === "dark";
    if (isDark) {
      document.documentElement.removeAttribute("data-theme");
      this.currentMode = "light";
    } else {
      document.documentElement.setAttribute("data-theme", "dark");
      this.currentMode = "dark";
    }
    this.saveMode(this.currentMode);
  }

  saveTheme(theme) {
    localStorage.setItem("clouvel-theme", theme);
  }

  getSavedTheme() {
    return localStorage.getItem("clouvel-theme");
  }

  saveMode(mode) {
    localStorage.setItem("clouvel-mode", mode);
  }

  getSavedMode() {
    return localStorage.getItem("clouvel-mode");
  }

  addSwitcherStyles() {
    const style = document.createElement("style");
    style.textContent = `
      .theme-switcher {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 1000;
      }

      .theme-switcher-toggle {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: var(--color-bg-secondary, #fff);
        border: 1px solid var(--color-border, #e5e7eb);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: all 0.2s;
      }

      .theme-switcher-toggle:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
      }

      .theme-switcher-toggle svg {
        color: var(--color-text-primary, #1f2937);
      }

      .theme-switcher-dropdown {
        position: absolute;
        bottom: 60px;
        right: 0;
        width: 240px;
        background: var(--color-bg-secondary, #fff);
        border: 1px solid var(--color-border, #e5e7eb);
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        opacity: 0;
        visibility: hidden;
        transform: translateY(10px);
        transition: all 0.2s;
      }

      .theme-switcher-dropdown.open {
        opacity: 1;
        visibility: visible;
        transform: translateY(0);
      }

      .theme-dropdown-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;
        border-bottom: 1px solid var(--color-border, #e5e7eb);
        font-weight: 600;
        font-size: 14px;
        color: var(--color-text-primary, #1f2937);
      }

      .dark-mode-toggle {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        border: 1px solid var(--color-border, #e5e7eb);
        background: var(--color-bg-tertiary, #f3f4f6);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s;
      }

      .dark-mode-toggle:hover {
        background: var(--color-accent-light, rgba(14, 165, 233, 0.1));
        border-color: var(--color-accent, #0ea5e9);
      }

      .dark-mode-toggle svg {
        color: var(--color-text-secondary, #6b7280);
      }

      .sun-icon { display: block; }
      .moon-icon { display: none; }

      [data-theme="dark"] .sun-icon { display: none; }
      [data-theme="dark"] .moon-icon { display: block; }

      .theme-options {
        padding: 8px;
      }

      .theme-option {
        width: 100%;
        padding: 10px 12px;
        border: none;
        background: transparent;
        border-radius: 8px;
        text-align: left;
        cursor: pointer;
        transition: all 0.15s;
        display: flex;
        flex-direction: column;
        gap: 2px;
      }

      .theme-option:hover {
        background: var(--color-bg-tertiary, #f3f4f6);
      }

      .theme-option.active {
        background: var(--color-accent-light, rgba(14, 165, 233, 0.1));
      }

      .theme-option.active .theme-name {
        color: var(--color-accent, #0ea5e9);
      }

      .theme-name {
        font-weight: 500;
        font-size: 14px;
        color: var(--color-text-primary, #1f2937);
      }

      .theme-desc {
        font-size: 12px;
        color: var(--color-text-secondary, #6b7280);
      }

      @media (max-width: 640px) {
        .theme-switcher {
          bottom: 16px;
          right: 16px;
        }

        .theme-switcher-toggle {
          width: 44px;
          height: 44px;
        }

        .theme-switcher-dropdown {
          width: 200px;
        }
      }
    `;
    document.head.appendChild(style);
  }
}

// Initialize on DOM ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => new ThemeSwitcher());
} else {
  new ThemeSwitcher();
}

// Export for manual control
window.ThemeSwitcher = ThemeSwitcher;
window.THEMES = THEMES;
