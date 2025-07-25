document.addEventListener("DOMContentLoaded", function () {
  const filter = document.querySelector("#statusFilter");
  const rows = document.querySelectorAll("table tbody tr");

  filter.addEventListener("change", () => {
    const value = filter.value;
    rows.forEach(row => {
      const status = row.querySelector("td.status").textContent.trim();
      row.style.display = (value === "All" || status === value) ? "" : "none";
    });
  });
});
