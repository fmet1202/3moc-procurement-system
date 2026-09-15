// Global recalculate fallback
document.addEventListener("DOMContentLoaded", function () {
  if (typeof recalculateAll === "function") {
    recalculateAll();
  }
});