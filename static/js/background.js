/*
 * Interactive Vanta.js NET background for the home page hero.
 * Skipped when the visitor prefers reduced motion or the libraries fail to load;
 * the hero then falls back to the CSS gradient defined in style.css.
 */
(function () {
  "use strict";

  var hero = document.getElementById("hero");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!hero || reduceMotion || !window.VANTA) return;

  // Colours are read from CSS custom properties so the theme lives in one place.
  var css = getComputedStyle(document.documentElement);
  function cssColor(name) {
    return parseInt(css.getPropertyValue(name).trim().replace("#", ""), 16);
  }

  var effect = window.VANTA.NET({
    el: hero,
    mouseControls: true,
    touchControls: true,
    gyroControls: false,
    minHeight: 200.0,
    minWidth: 200.0,
    scale: 1.0,
    scaleMobile: 1.0,
    color: cssColor("--hero-accent"),
    backgroundColor: cssColor("--hero-bg"),
    points: 11.0,
    maxDistance: 22.0,
    spacing: 17.0
  });
  hero.classList.add("has-vanta");

  window.addEventListener("pagehide", function () { effect.destroy(); });
})();
