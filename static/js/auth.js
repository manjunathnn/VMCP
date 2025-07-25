document.addEventListener("DOMContentLoaded", function () {
  const togglePw = document.querySelector("#togglePassword");
  const passwordField = document.querySelector("#password");

  if (togglePw && passwordField) {
    togglePw.addEventListener("click", () => {
      const type = passwordField.type === "password" ? "text" : "password";
      passwordField.type = type;
      togglePw.textContent = type === "text" ? "Hide" : "Show";
    });
  }
});
