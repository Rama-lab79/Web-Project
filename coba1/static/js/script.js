// Fungsi untuk toggle menu burger
function setupBurgerMenu() {
  const burger = document.querySelector(".burger-menu");
  const navMenu = document.querySelector(".nav-menu");

  if (burger && navMenu) {
    burger.addEventListener("click", function () {
      this.classList.toggle("active");
      navMenu.classList.toggle("active");

      // Toggle overflow pada body saat menu aktif
      if (navMenu.classList.contains("active")) {
        document.body.style.overflow = "hidden";
      } else {
        document.body.style.overflow = "auto";
      }
    });

    // Tutup menu saat mengklik link
    const navLinks = document.querySelectorAll(".nav-menu a");
    navLinks.forEach((link) => {
      link.addEventListener("click", function () {
        burger.classList.remove("active");
        navMenu.classList.remove("active");
        document.body.style.overflow = "auto";
      });
    });
  }
}

// Gallery Functionality (Dengan pengecekan elemen)
// Hero Auto Slider
function setupHeroSlider() {
  const slides = document.querySelectorAll(".slide");
  if (slides.length === 0) return;

  let currentIndex = 0;

  function showSlide(index) {
    slides.forEach((slide, i) => {
      slide.classList.remove("opacity-100", "opacity-0", "active");
      slide.classList.add("opacity-0");
      if (i === index) {
        slide.classList.add("opacity-100", "active");
      }
    });
  }

  function nextSlide() {
    currentIndex = (currentIndex + 1) % slides.length;
    showSlide(currentIndex);
  }

  // Jalankan auto slide setiap 5 detik
  setInterval(nextSlide, 5000);
  showSlide(currentIndex);
}

setupHeroSlider(); // Aktifkan auto slider untuk hero

// Panggil fungsi saat DOM siap
document.addEventListener("DOMContentLoaded", function () {
  setupBurgerMenu(); // Navigasi
  setupGallery(); // Galeri
  setupHeroSlider(); // Hero auto-slide
});
