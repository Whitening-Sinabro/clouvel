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
    submitBtn.innerHTML = "<span>Sending...</span>";

    const email = document.getElementById("email").value;
    const issueType = document.getElementById("issueType").value;
    const message = document.getElementById("message").value;

    const issueTypeLabels = {
      machine_reset: "Machine Reset / New PC",
      license_issue: "License Issue",
      bug_report: "Bug Report",
      feature_request: "Feature Request",
      other: "Other",
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
      '<span>Send Inquiry</span><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>';
  });

// Mobile Menu Toggle
const mobileMenuBtn = document.getElementById("mobileMenuBtn");
const mobileMenu = document.getElementById("mobileMenu");

if (mobileMenuBtn && mobileMenu) {
  mobileMenuBtn.addEventListener("click", () => {
    mobileMenu.classList.toggle("hidden");
  });

  mobileMenu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      mobileMenu.classList.add("hidden");
    });
  });
}
