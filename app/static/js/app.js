document.addEventListener("DOMContentLoaded", function () {
  const dateInput = document.querySelector('input[name="date"]');
  if (dateInput && !dateInput.value) {
    dateInput.value = new Date().toISOString().slice(0, 10);
  }
});
