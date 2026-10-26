(function () {
  "use strict";

  var header = document.getElementById("header");
  var nav = document.getElementById("nav");
  var toggle = document.getElementById("navToggle");

  // Solid header after scrolling past the top
  function onScroll() {
    header.classList.toggle("solid", window.scrollY > 40);
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  // Mobile menu
  toggle.addEventListener("click", function () {
    var open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });
  nav.addEventListener("click", function (e) {
    if (e.target.closest("a") && nav.classList.contains("open")) {
      nav.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });

  // Dropdowns (click/tap + Escape)
  var dropdowns = document.querySelectorAll(".dropdown");
  dropdowns.forEach(function (dd) {
    var btn = dd.querySelector(".dropdown-btn");
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var willOpen = !dd.classList.contains("open");
      dropdowns.forEach(function (o) {
        o.classList.remove("open");
        o.querySelector(".dropdown-btn").setAttribute("aria-expanded", "false");
      });
      dd.classList.toggle("open", willOpen);
      btn.setAttribute("aria-expanded", String(willOpen));
    });
  });
  document.addEventListener("click", function () {
    dropdowns.forEach(function (o) {
      o.classList.remove("open");
      o.querySelector(".dropdown-btn").setAttribute("aria-expanded", "false");
    });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      dropdowns.forEach(function (o) { o.classList.remove("open"); });
      nav.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });

  // Footer year
  var year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();

  // Checklist sign-up.
  // Set data-endpoint on #signup (in index.html) to your form service URL.
  // Until then the form does NOT collect addresses and says so honestly.
  var form = document.getElementById("signup");
  var msg = document.getElementById("formMsg");
  if (form) form.addEventListener("submit", function (e) {
    e.preventDefault();
    var email = form.elements.email.value.trim();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      msg.textContent = "Please enter a valid email address.";
      return;
    }
    var endpoint = form.getAttribute("data-endpoint");
    if (!endpoint) {
      msg.textContent = "Sign-ups open soon. Please check back shortly.";
      return;
    }
    msg.textContent = "Sending…";
    fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ email: email, source: "discoverdolomites.org" })
    }).then(function (r) {
      if (!r.ok) throw new Error("bad status");
      form.reset();
      msg.textContent = "Thank you. Check your inbox for the checklist.";
    }).catch(function () {
      msg.textContent = "Something went wrong. Please try again.";
    });
  });
})();
