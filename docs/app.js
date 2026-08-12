const switcher = document.querySelector(".proof-switcher");

if (switcher) {
  const controls = [...switcher.querySelectorAll("[data-view]")];
  const values = [...switcher.querySelectorAll("dd[data-before][data-after]")];
  const statusLabel = switcher.querySelector(".status-label");
  const statusCount = switcher.querySelector(".status-count");

  const setView = (view) => {
    switcher.dataset.state = view;
    controls.forEach((control) => {
      control.setAttribute("aria-pressed", String(control.dataset.view === view));
    });

    values.forEach((value, index) => {
      value.animate(
        [
          { opacity: 0, transform: "translateY(0.4rem)" },
          { opacity: 1, transform: "translateY(0)" },
        ],
        { duration: 220, delay: index * 35, easing: "ease-out" },
      );
      value.textContent = value.dataset[view];
    });

    statusLabel.textContent = view === "after" ? "RESCUED CONTRACT" : "BROKEN CONTRACT";
    statusCount.textContent = view === "after" ? "6 / 6 checks pass" : "5 visible failures";
  };

  controls.forEach((control) => {
    control.addEventListener("click", () => setView(control.dataset.view));
  });
}

const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12 },
);

document.querySelectorAll(".reveal").forEach((element) => revealObserver.observe(element));

