document.addEventListener("DOMContentLoaded", function () {
  const stateSelect = document.querySelector("#state");
  const districtSelect = document.querySelector("#district");

  stateSelect.addEventListener("change", function () {
    const state = stateSelect.value;
    fetch(`/api/districts?state=${state}`)
      .then(res => res.json())
      .then(data => {
        districtSelect.innerHTML = "";
        data.districts.forEach(dist => {
          const option = document.createElement("option");
          option.value = dist;
          option.textContent = dist;
          districtSelect.appendChild(option);
        });
      });
  });
});
