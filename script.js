document.documentElement.classList.add("js-enabled");
const navToggle = document.querySelector("[data-nav-toggle]");
const nav = document.querySelector("[data-nav]");
const year = document.querySelector("[data-year]");

if (year) {
  year.textContent = new Date().getFullYear();
}

if (navToggle && nav) {
  const closeNav = () => {
    navToggle.setAttribute("aria-expanded", "false");
    nav.classList.remove("is-open");
  };

  navToggle.addEventListener("click", () => {
    const isOpen = navToggle.getAttribute("aria-expanded") === "true";
    navToggle.setAttribute("aria-expanded", String(!isOpen));
    nav.classList.toggle("is-open", !isOpen);
  });

  nav.addEventListener("click", (event) => {
    if (event.target instanceof HTMLAnchorElement) {
      closeNav();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      const hadFocus = nav.contains(document.activeElement);
      closeNav();
      if (hadFocus) navToggle.focus();
    }
  });

  document.addEventListener("click", (event) => {
    if (!nav.contains(event.target) && !navToggle.contains(event.target)) {
      closeNav();
    }
  });
}

document.addEventListener("click", (event) => {
  const link = event.target instanceof Element ? event.target.closest("a") : null;

  if (!(link instanceof HTMLAnchorElement) || typeof window.gtag !== "function") {
    return;
  }

  const eventName = link.href.startsWith("tel:")
    ? "phone_click"
    : link.dataset.booking || ((link.hostname === "kmuh.org.tw" || link.hostname.endsWith(".kmuh.org.tw")) && link.href.includes("Registration"))
      ? "booking_click"
      : null;

  if (eventName) {
    window.gtag("event", eventName, {
      link_url: link.protocol === "tel:" ? link.href : link.origin + link.pathname,
      page_path: window.location.pathname,
      booking_destination: link.dataset.booking || "hospital"
    });
  }
});

// Progressive enhancement: every article and link is present in the HTML.
// Search is local only; queries are not stored or sent to another service.
const library = document.querySelector("[data-article-library]");
if (library) {
  const controls = library.querySelector("[data-library-controls]");
  const search = library.querySelector("[data-article-search]");
  const filters = [...library.querySelectorAll("[data-article-filter]")];
  const cards = [...library.querySelectorAll("[data-article-category]")];
  const status = library.querySelector("[data-search-status]");
  const empty = library.querySelector("[data-search-empty]");
  let category = "all";
  const normalize = (text) => text.normalize("NFKC").toLocaleLowerCase().trim();
  const update = () => {
    const words = normalize(search.value).split(/\s+/).filter(Boolean);
    let count = 0;
    cards.forEach((card) => {
      const text = normalize(card.textContent + " " + (card.dataset.searchTerms || ""));
      const matches = (category === "all" || card.dataset.articleCategory === category)
        && words.every((word) => text.includes(word));
      card.hidden = !matches;
      if (matches) count++;
    });
    filters.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.articleFilter === category)));
    status.textContent = `顯示 ${count} 篇，共 ${cards.length} 篇衛教與就醫指南`;
    empty.hidden = count !== 0;
  };
  filters.forEach((button) => button.addEventListener("click", () => {
    category = button.dataset.articleFilter;
    update();
  }));
  search.addEventListener("input", update);
  library.querySelector("[data-search-reset]").addEventListener("click", () => {
    category = "all";
    search.value = "";
    update();
    search.focus();
  });
  controls.hidden = false;
  update();
}
