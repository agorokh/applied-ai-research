/** Sync aria-expanded on CSS hover/focus Reports dropdowns. */
for (const nav of document.querySelectorAll(".rs-nav-reports")) {
  const trigger = nav.querySelector(".rs-nav-reports__trigger");
  if (!trigger) continue;
  trigger.setAttribute("aria-expanded", "false");
  const setOpen = (open) =>
    trigger.setAttribute("aria-expanded", open ? "true" : "false");
  nav.addEventListener("mouseenter", () => setOpen(true));
  nav.addEventListener("mouseleave", () => setOpen(false));
  nav.addEventListener("focusin", () => setOpen(true));
  nav.addEventListener("focusout", (event) => {
    if (!nav.contains(event.relatedTarget)) setOpen(false);
  });
}
