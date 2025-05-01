document.addEventListener('DOMContentLoaded', () => {
  const inputField = document.getElementById('search-input');
  const dropdownMenu = document.getElementById('live-results');
  const modelSelect = document.getElementById('model-select'); // Get the model dropdown

  inputField.addEventListener('input', () => {
    const query = inputField.value.trim();
    const selectedModel = modelSelect.value; // Get the current model selection
    
    if (!query) {
      // Clear and hide the dropdown
      dropdownMenu.innerHTML = "";
      dropdownMenu.style.display = "none";
      return;
    }

    // Include the model parameter in the API call
    fetch(`/live-search-api/?q=${encodeURIComponent(query)}&model=${encodeURIComponent(selectedModel)}`)
      .then((response) => response.json())
      .then((data) => {
        renderDropdown(data, query, selectedModel);
      })
      .catch((err) => console.error("Error fetching live search results:", err));
  });

  function renderDropdown(data, query, selectedModel) {
    if (!data.length) {
      dropdownMenu.innerHTML = "<p class='no-suggestions'>No results</p>";
      dropdownMenu.style.display = "block";
      return;
    }
    dropdownMenu.innerHTML = `
      <ul class='suggestion-list'>
        ${data.map(item => `
          <li class="suggestion-item">
            <a href="/search/?query=${encodeURIComponent(item.chemName)}&model=${encodeURIComponent(selectedModel)}" class="dropdown-link">
              ${highlightQuery(item.chemName, query)} (ID: ${item.chemID || item.chemBottleIDNUM})
            </a>
          </li>
        `).join('')}
      </ul>
    `;
    dropdownMenu.style.display = "block";
  }

  function highlightQuery(text, query) {
    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const regex = new RegExp(`^(${escapedQuery})`, "i"); 
    return text.replace(regex, (match) => `<mark>${match}</mark>`);
  }
});