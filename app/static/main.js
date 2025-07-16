// 1) Utility to submit a POST with optional confirmation and extra data
function postForm(path, confirmMessage = null, extraData = {}) {
  if (confirmMessage && !window.confirm(confirmMessage)) return;
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = path;
  Object.entries(extraData).forEach(([name, value]) => {
    const input = document.createElement('input');
    input.type  = 'hidden';
    input.name  = name;
    input.value = value;
    form.append(input);
  });
  document.body.append(form);
  form.submit();
}

// 2) Utility to reload the page with a new user_id
function loadIndex({ user_id }) {
  window.location = `?user_id=${user_id}`;
}

// 3) Utility to fetch a partial and display it in the global modal
async function openModal(url) {
  const res  = await fetch(url);
  const html = await res.text();
  const modalEl  = document.getElementById('globalModal');
  modalEl.querySelector('.modal-content').innerHTML = html;
  new bootstrap.Modal(modalEl).show();
  bindMovieModal();  // bind our movie‐search/add logic if this is the movie modal
}

// 4) Delegate “Add Movie” and “Add to Favourites” inside the modal
function bindMovieModal() {
  const modalEl = document.getElementById('globalModal');
  if (!modalEl) return;

  // Get the form and results container
  const form = modalEl.querySelector('#addMovieForm');
  const resultsContainer = modalEl.querySelector('#movieSearchResults');
  if (!form || !resultsContainer) return;

  // Unbind any prior submit handler
  form.onsubmit = null;

  // Handle “Search” (GET + re-inject into same modal)
  form.addEventListener('submit', async e => {
    e.preventDefault();                         // prevent full-page reload
    const title = form.querySelector('[name=title]').value.trim();
    const userId = form.dataset.userId;
    if (!title || !userId) return;

    // Fetch the same template with data
    const url = `/users/${userId}/movies?modal=1&action=add&title=${encodeURIComponent(title)}`;
    const res = await fetch(url);
    const html = await res.text();

    // Replace only the modal-content so it stays open
    modalEl.querySelector('.modal-content').innerHTML = html;
    new bootstrap.Modal(modalEl).show();

    // Re-bind this logic to the newly injected HTML
    bindMovieModal();
  });

  // Handle “Add to Favourites” click
  const addBtn = modalEl.querySelector('#addToFavBtn');
  if (addBtn) {
    addBtn.onclick = () => {
      const userId = form.dataset.userId;
      // read the title from the card-title element
      const titleText = modalEl.querySelector('.card-title')?.textContent.trim();
      if (!userId || !titleText) return;
      postForm(`/users/${userId}/movies`, null, { title: titleText });
    };
  }
}

// 5) Wire up any “js-open-modal” buttons on page load
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.js-open-modal').forEach(btn => {
    btn.addEventListener('click', () => openModal(btn.dataset.url));
  });
  // Also bind in case the modal was already open with movie-form
  bindMovieModal();

  // 6) Utility: Bind Delete‐Buttons auf der Index‐Page
  document.querySelectorAll('.js-delete-movie').forEach(btn => {
    btn.addEventListener('click', () => {
      postForm(btn.dataset.url, 'Do you really want to delete this movie?');
    });
  });
});

