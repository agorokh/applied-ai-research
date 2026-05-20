/**
 * Reports ▾ dropdown — sync aria-expanded on CSS hover/focus, plus a click
 * toggle so touch users (no :hover state on mobile) can open the panel.
 *
 * The visible-open behaviour is owned by CSS (.rs-nav-reports:hover and
 * .rs-nav-reports:focus-within); this script just keeps aria-expanded
 * truthful and adds an .is-open class the CSS uses as a third
 * open-condition for click-driven (touch) interactions.
 */
for (const nav of document.querySelectorAll(".rs-nav-reports")) {
  const trigger = nav.querySelector(".rs-nav-reports__trigger");
  if (!trigger) continue;

  trigger.setAttribute("aria-expanded", "false");

  const setOpen = (open) => {
    nav.classList.toggle("is-open", open);
    trigger.setAttribute("aria-expanded", open ? "true" : "false");
  };

  // Hover + focus mirror the CSS-driven state for screen-readers.
  nav.addEventListener("mouseenter", () => setOpen(true));
  nav.addEventListener("mouseleave", () => setOpen(false));
  nav.addEventListener("focusin", () => setOpen(true));
  nav.addEventListener("focusout", (event) => {
    if (!nav.contains(event.relatedTarget)) setOpen(false);
  });

  // Click toggle — required for touch devices where :hover never fires.
  trigger.addEventListener("click", (event) => {
    event.preventDefault();
    const isOpen = trigger.getAttribute("aria-expanded") === "true";
    setOpen(!isOpen);
  });

  // Click outside the nav closes the panel (touch + desktop).
  document.addEventListener("click", (event) => {
    if (!nav.contains(event.target)) setOpen(false);
  });

  // Escape key closes the panel and returns focus to the trigger.
  nav.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      setOpen(false);
      trigger.focus();
    }
  });
}
