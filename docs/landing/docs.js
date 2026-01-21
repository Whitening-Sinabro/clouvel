/* Clouvel Docs Page JavaScript */

// Active sidebar link on scroll
const sections = document.querySelectorAll("section[id]");
const sidebarLinks = document.querySelectorAll(".sidebar-link");

window.addEventListener("scroll", () => {
  let current = "";
  sections.forEach((section) => {
    const sectionTop = section.offsetTop;
    if (scrollY >= sectionTop - 100) {
      current = section.getAttribute("id");
    }
  });

  sidebarLinks.forEach((link) => {
    link.classList.remove("active");
    if (link.getAttribute("href") === "#" + current) {
      link.classList.add("active");
    }
  });
});
