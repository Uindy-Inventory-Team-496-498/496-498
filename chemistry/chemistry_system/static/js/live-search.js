document.addEventListener('DOMContentLoaded', () => {
    const inputField = document.getElementById('search-input');
    const dropdownMenu = document.getElementById('live-results');
  
    inputField.addEventListener('input', () => {
      const query = inputField.value.trim();
      if (!query) {
        // Clear and hide the dropdown
        dropdownMenu.innerHTML = "";
        dropdownMenu.style.display = "none";
        return;
      }
  
      // Call your live-search API endpoint
      fetch(`/live-search-api/?q=${encodeURIComponent(query)}`)
        .then((response) => response.json())
        .then((data) => {
          renderDropdown(data, query);
        })
        .catch((err) => console.error("Error fetching live search results:", err));
    });
  
    /**
     * Renders the dropdown suggestions list.
     * @param {Array} data - Array of objects [{chemName, chemBottleIDNUM}, ...].
     * @param {string} query - The user’s typed string.
     */
    function highlightQuery(text, query) {
        const regex = new RegExp(`^(${query})`, "i"); 
        return text.replace(regex, (match) => `<mark>${match}</mark>`);
      }
      
      function renderDropdown(data, query) {
        if (!data.length) {
          dropdownMenu.innerHTML = "<p class='no-suggestions'>No results</p>";
          dropdownMenu.style.display = "block";
          return;
        }
        dropdownMenu.innerHTML = `
          <ul class='suggestion-list'>
            ${data.map(item => `
              <li class="suggestion-item">
                <a href="/search/?query=${encodeURIComponent(item.chemName)}" class="dropdown-link">
                  ${highlightQuery(item.chemName, query)} (ID: ${item.chemBottleIDNUM})
                </a>
              </li>
            `).join('')}
          </ul>
        `;
        dropdownMenu.style.display = "block";
      }
      
  
    /**
     * Highlights the portion of the item’s name that matches the user’s query.
     * For a simple highlight, we’ll do a case-insensitive search for “starts with.”
     */
    function highlightQuery(text, query) {
      const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); // escape special chars
      const regex = new RegExp(`^(${escapedQuery})`, "i"); 
      return text.replace(regex, (match) => `<mark>${match}</mark>`);
    }
  });
  