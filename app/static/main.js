// File: app/blueprints/static/js/utils.js
/**
 * Purpose:
 *   Provide utility functions for form submission, page navigation,
 *   and modal handling in the application UI.
 *
 * Features:
 *   - Submit POST requests with optional confirmation and extra data
 *   - Reload page with updated query parameters
 *   - Load and display HTML fragments in a global Bootstrap modal
 *   - Bind movie search/add and delete actions dynamically
 *   - Clean up modal backdrops and state upon closing
 *
 * Dependencies:
 *   - window.fetch API
 *   - Bootstrap Modal (bootstrap.Modal)
 *   - DOM APIs: document, window, Element
 *
 * Author: Martin Haferanke
 *
 * Date: 2025-07-18
 */

/**
 * Submit a POST request by creating and submitting a hidden form.
 *
 * @param {string} path - URL to submit the form to.
 * @param {string|null} [confirmMessage=null] - Optional confirmation message.
 * @param {Object} [extraData={}] - Key-value pairs to include as hidden inputs.
 * @throws {Error} Throws when form submission fails.
 */
function postForm(path, confirmMessage = null, extraData = {}) {
  if (confirmMessage && !window.confirm(confirmMessage)) return;
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = path;
  Object.entries(extraData).forEach(([name, value]) => {
    const input = document.createElement('input');
    input.type  = 'hidden';
    input.name  = name;
    input.value = String(value);
    form.append(input);
  });
  document.body.append(form);
  form.submit();
}


/**
 * Reload the current page with updated query parameters.
 *
 * @param {{user_id: number}} params - Object containing new query params.
 */
function loadIndex({ user_id }) {
  window.location = `?user_id=${user_id}`;
}


/**
 * Fetch an HTML fragment from the server and display it in the global modal.
 *
 * @param {string} url - Endpoint to fetch HTML fragment from.
 * @returns {Promise<void>}
 * @throws {Error} Throws when network or parsing fails.
 */
async function openModal(url) {
  const res  = await fetch(url);
  const html = await res.text();
  const modalEl  = document.getElementById('globalModal');
  modalEl.querySelector('.modal-content').innerHTML = html;
  new bootstrap.Modal(modalEl).show();
  bindMovieModal();
}


/**
 * Close the global modal and remove backdrop elements.
 */
function closeModal() {
  const modalEl = document.getElementById('globalModal');
  const bsModal = bootstrap.Modal.getInstance(modalEl);
  if (bsModal) bsModal.hide();
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
  document.body.classList.remove('modal-open');
}



// Bind form submission and button actions inside the movie modal.
function bindMovieModal() {
  const modalEl = document.getElementById('globalModal');
  if (!modalEl) return;

  const form = modalEl.querySelector('#addMovieForm');
  const resultsContainer = modalEl.querySelector('#movieSearchResults');
  if (!form || !resultsContainer) return;

  form.onsubmit = null;

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const title = form.querySelector('[name=title]').value.trim();
    const userId = form.dataset.userId;
    if (!title || !userId) return;

    const url = `/users/${userId}/movies?modal=1&action=add&title=${encodeURIComponent(title)}`;
    const res = await fetch(url);
    const html = await res.text();

    modalEl.querySelector('.modal-content').innerHTML = html;
    new bootstrap.Modal(modalEl).show();

    bindMovieModal();
  });

  const addBtn = modalEl.querySelector('#addToFavBtn');
  if (addBtn) {
    addBtn.onclick = () => {
      const userId = form.dataset.userId;
      const titleText = modalEl.querySelector('.card-title')?.textContent.trim();
      if (!userId || !titleText) return;
      postForm(`/users/${userId}/movies`, null, { title: titleText });
    };
  }
}


// Wire up buttons, delete actions on a page load and attach closeModal action inside the modal
document.addEventListener('DOMContentLoaded', () => {

  const globalModalEl = document.getElementById('globalModal');
  globalModalEl.addEventListener('click', e => {
    if (e.target.closest('[data-bs-dismiss="modal"]')) {
      closeModal();
    }
  });

  document.querySelectorAll('.js-open-modal').forEach(btn => {
    btn.addEventListener('click', () => openModal(btn.dataset.url));
  });
  bindMovieModal();

  document.querySelectorAll('.js-delete-movie').forEach(btn => {
    btn.addEventListener('click', () => {
      postForm(btn.dataset.url, 'Do you really want to delete this movie?');
    });
  });

});