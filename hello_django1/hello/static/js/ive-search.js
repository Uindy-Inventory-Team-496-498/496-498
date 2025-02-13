document.addEventListener('DOMContentLoaded', () => {
    const inputField = document.getElementById('search-input');
    const dropdownMenu = document.getElementById('live-results');

    inputField.addEventListener('input', () => {
        const query = inputField.value.trim();
        if (!query) {
            dropdownMenu.innerHTML = "";
            dropdownMenu.style.display = "none";
            return;
        }

        fetch(`/live-search-api/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                renderDropdown(data, query);
            })
            .catch(err => console.error("Error fetching live search results:", err));
    });

    function renderDropdown(data, query) {
        if (data.length === 0) {
            dropdownMenu.innerHTML = "<p class='no-suggestions'>No suggestions found</p>";
            dropdownMenu.style.display = "block";
            return;
        }
    
        dropdownMenu.innerHTML = `
            <ul class='suggestion-list'>
                ${data
                    .map(
                        (item) =>
                            `<li class="suggestion-item">
                                <a href="/search/?query=${item.chemName}" class="dropdown-link">
                                    <span class="chem-name">${highlightQuery(item.chemName, query)}</span>
                                    <span class="chem-id">(ID: ${item.chemBottleIDNUM})</span>
                                </a>
                            </li>`
                    )
                    .join("")}
            </ul>
        `;
        dropdownMenu.style.display = "block";
    
        // Ensure dropdown width matches input width
        dropdownMenu.style.width = inputField.offsetWidth + "px";
    }
    
    function highlightQuery(text, query) {
        if (!text.toLowerCase().startsWith(query.toLowerCase())) {
            return text; // If the word doesn't start with the query, return unchanged
        }

        const boldPart = text.substring(0, query.length);  // Extract the matched part
        const normalPart = text.substring(query.length);   // Extract the rest

        return `<strong style="color: black;">${boldPart}</strong>${normalPart}`; // Bold only the start
    }
    
});
