document.addEventListener("DOMContentLoaded", () => {
  // Bulma - Navbar Burger
  // Get all "navbar-burger" elements
  const $navbarBurgers = Array.prototype.slice.call(
    document.querySelectorAll(".navbar-burger"),
    0
  );

  // Check if there are any navbar burgers
  if ($navbarBurgers.length > 0) {
    // Add a click event on each of them
    $navbarBurgers.forEach((el) => {
      el.addEventListener("click", () => {
        // Get the target from the "data-target" attribute
        const target = el.dataset.target;
        const $target = document.getElementById(target);

        // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
        el.classList.toggle("is-active");
        $target.classList.toggle("is-active");
      });
    });
  }

  // Back To Top Button
  var btn = document.querySelector("#back-to-top");
  window.addEventListener("scroll", function () {
    if (
      document.documentElement.scrollTop > 30 ||
      document.body.scrollTop > 30
      // && !document.querySelector("modal").classList.contains("is-active")
    ) {
      btn.classList.add("show");
    } else {
      btn.classList.remove("show");
    }
  });

  // Modal
  var modal = document.querySelector(".modal");
  document.querySelector(".modal-button").addEventListener("click", () => {
    modal.classList.add("is-active");
  });

  var cancel = document.getElementsByClassName("cancel");
  for (var i = 0; i < cancel.length; ++i)
    cancel[i].addEventListener("click", () => {
      modal.classList.remove("is-active");
    });
});
