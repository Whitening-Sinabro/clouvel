/* Clouvel Landing Page JavaScript */

// Contact Form Handler
document
  .getElementById("contactForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const submitBtn = document.getElementById("submitBtn");
    const formSuccess = document.getElementById("formSuccess");
    const formError = document.getElementById("formError");

    formSuccess.classList.add("hidden");
    formError.classList.add("hidden");
    submitBtn.disabled = true;
    submitBtn.innerHTML = "<span>전송 중...</span>";

    const email = document.getElementById("email").value;
    const issueType = document.getElementById("issueType").value;
    const message = document.getElementById("message").value;

    const issueTypeLabels = {
      machine_reset: "PC 교체 / 머신 리셋",
      license_issue: "라이선스 문제",
      bug_report: "버그 리포트",
      feature_request: "기능 요청",
      other: "기타",
    };

    const webhookUrl =
      "https://discord.com/api/webhooks/1462105007804645468/JWNks6MBwpBOMeWj3nWFo6wwE3SpsXUZ8KMUVw9riBUR3uvETvLNSxSW4VU69fJ31w_2";

    const payload = {
      embeds: [
        {
          title: "New Contact",
          color: 0x0ea5e9,
          fields: [
            { name: "Email", value: email, inline: true },
            {
              name: "Type",
              value: issueTypeLabels[issueType] || issueType,
              inline: true,
            },
            { name: "Message", value: message || "(none)", inline: false },
          ],
          timestamp: new Date().toISOString(),
        },
      ],
    };

    try {
      const response = await fetch(webhookUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        formSuccess.classList.remove("hidden");
        document.getElementById("contactForm").reset();
      } else {
        formError.classList.remove("hidden");
      }
    } catch (error) {
      formError.classList.remove("hidden");
    }

    submitBtn.disabled = false;
    submitBtn.innerHTML =
      '<span>문의 보내기</span><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>';
  });

// Mobile Menu Toggle
const mobileMenuBtn = document.getElementById("mobileMenuBtn");
const mobileMenu = document.getElementById("mobileMenu");

mobileMenuBtn.addEventListener("click", () => {
  mobileMenu.classList.toggle("hidden");
});

// Close menu when clicking a link
mobileMenu.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    mobileMenu.classList.add("hidden");
  });
});

// Tab Switching
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    // Remove active from all buttons
    document.querySelectorAll(".tab-btn").forEach((b) => {
      b.classList.remove("active");
      b.classList.add("bg-slate-700");
    });
    // Add active to clicked button
    btn.classList.add("active");
    btn.classList.remove("bg-slate-700");

    // Hide all tab contents
    document.querySelectorAll(".tab-content").forEach((content) => {
      content.classList.remove("active");
    });
    // Show selected tab content
    const tabId = "tab-" + btn.dataset.tab;
    document.getElementById(tabId).classList.add("active");
  });
});

// Pricing Billing Toggle
function toggleBilling(type) {
  const monthlyBtn = document.getElementById("monthly-btn");
  const yearlyBtn = document.getElementById("yearly-btn");
  const monthlyPrices = document.querySelectorAll(".monthly-price");
  const yearlyPrices = document.querySelectorAll(".yearly-price");
  const checkoutLinks = document.querySelectorAll(".checkout-link");

  if (type === "monthly") {
    // Update button styles
    monthlyBtn.classList.add("bg-white", "text-dark-slate", "shadow-sm");
    monthlyBtn.classList.remove("text-slate-500");
    yearlyBtn.classList.remove("bg-white", "text-dark-slate", "shadow-sm");
    yearlyBtn.classList.add("text-slate-500");

    // Show monthly, hide yearly
    monthlyPrices.forEach((el) => el.classList.remove("hidden"));
    yearlyPrices.forEach((el) => el.classList.add("hidden"));

    // Update checkout links to monthly
    checkoutLinks.forEach((link) => {
      if (link.dataset.monthly) {
        link.href = link.dataset.monthly;
      }
    });
  } else {
    // Update button styles
    yearlyBtn.classList.add("bg-white", "text-dark-slate", "shadow-sm");
    yearlyBtn.classList.remove("text-slate-500");
    monthlyBtn.classList.remove("bg-white", "text-dark-slate", "shadow-sm");
    monthlyBtn.classList.add("text-slate-500");

    // Show yearly, hide monthly
    yearlyPrices.forEach((el) => el.classList.remove("hidden"));
    monthlyPrices.forEach((el) => el.classList.add("hidden"));

    // Update checkout links to yearly
    checkoutLinks.forEach((link) => {
      if (link.dataset.yearly) {
        link.href = link.dataset.yearly;
      }
    });
  }
}

// Store original monthly links on load
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".checkout-link").forEach((link) => {
    link.dataset.monthly = link.href;
  });
});

// Make toggleBilling globally available
window.toggleBilling = toggleBilling;
