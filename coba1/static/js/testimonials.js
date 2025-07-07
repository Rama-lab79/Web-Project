document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("testimonialForm");
  const testimonialsContainer = document.getElementById(
    "testimonialsContainer"
  );

  if (!form || !testimonialsContainer) {
    console.warn("Elemen form atau container testimoni tidak ditemukan.");
    return;
  }

  // Fungsi bikin kartu testimonial
  function createTestimonialCard(testimonial) {
    const card = document.createElement("div");
    card.className = "testimonial-card bg-white p-4 rounded shadow mb-4";
    card.setAttribute("data-id", testimonial.id);

    card.innerHTML = `
      <h4 class="font-bold text-lg">${testimonial.title}</h4>
      <p class="text-gray-700 mt-1 mb-2">"${testimonial.message}"</p>
      <p class="text-sm text-gray-500 mb-3">- ${testimonial.name}, ${
      testimonial.date
    }</p>
      <div class="flex gap-2">
        <button onclick="openEditModal(${
          testimonial.id
        }, '${testimonial.name.replace(
      /'/g,
      "\\'"
    )}', '${testimonial.title.replace(
      /'/g,
      "\\'"
    )}', \`${testimonial.message.replace(
      /`/g,
      "\\`"
    )}\`)" class="bg-yellow-500 text-white px-3 py-1 rounded text-sm">Edit</button>
        <button onclick="deleteTestimonial(${
          testimonial.id
        })" class="bg-red-600 text-white px-3 py-1 rounded text-sm">Hapus</button>
      </div>
    `;

    return card;
  }

  // Kirim testimonial baru
  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    try {
      const response = await fetch("/submit_testimonial", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: document.getElementById("name").value,
          title: document.getElementById("title").value,
          message: document.getElementById("message").value,
        }),
      });

      const data = await response.json();

      if (data.status === "success") {
        form.reset();
        const newCard = createTestimonialCard(data.testimonial);
        testimonialsContainer.prepend(newCard);
        alert("Testimonial berhasil dikirim!");
      } else {
        alert(
          "Gagal mengirim testimonial: " + (data.message || "Unknown error")
        );
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Terjadi kesalahan. Silakan coba lagi.");
    }
  });
});

// 🛠️ FUNGSI EDIT DAN DELETE GLOBAAAAAAL 🔥
let editId = null;

function openEditModal(id, name, title, message) {
  editId = id;
  document.getElementById("editName").value = name;
  document.getElementById("editTitle").value = title;
  document.getElementById("editMessage").value = message;
  document.getElementById("editModal").classList.remove("hidden");
}

function closeEditModal() {
  document.getElementById("editModal").classList.add("hidden");
}

function submitEdit() {
  const name = document.getElementById("editName").value;
  const title = document.getElementById("editTitle").value;
  const message = document.getElementById("editMessage").value;

  fetch(`/update_testimonial/${editId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name, title, message }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        location.reload();
      } else {
        alert("Gagal memperbarui testimoni");
      }
    });
}

function deleteTestimonial(id) {
  if (!confirm("Yakin ingin menghapus testimoni ini?")) return;

  fetch(`/delete_testimonial/${id}`, {
    method: "DELETE",
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        location.reload();
      } else {
        alert("Gagal menghapus testimoni");
      }
    });
}
