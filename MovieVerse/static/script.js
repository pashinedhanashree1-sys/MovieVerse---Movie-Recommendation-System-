/**
 * script.js - Home page behavior.
 *
 * Clicking "Recommend" (or pressing Enter in the search box) now navigates
 * to a real page: /recommendations?movie=<name>. Flask renders that page
 * server-side, so refresh and browser back/forward both work correctly
 * with zero extra client-side state management.
 */

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("recommendBtn");
  const input = document.getElementById("searchInput");
  const overlay = document.getElementById("loadingOverlay");

  function goToRecommendations() {
    const movie = input.value.trim();

    if (movie === "") {
      alert("Please enter a movie name!");
      return;
    }

    if (overlay) {
      overlay.classList.add("show");
    }
    btn.disabled = true;

    // A tiny delay lets the loading overlay actually paint before the
    // browser starts navigating away.
    window.setTimeout(() => {
      window.location.href = `/recommendations?movie=${encodeURIComponent(movie)}`;
    }, 150);
  }

  btn.addEventListener("click", goToRecommendations);

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      goToRecommendations();
    }
  });
});