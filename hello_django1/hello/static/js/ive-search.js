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
        dropdownMenu.style.width = inputField.offsetWidth + "px"; // Match width
    }

    function highlightQuery(text, query) {
        const regex = new RegExp(`^(${query})`, "i"); // Match only the beginning of the word
        return text.replace(regex, `<strong style="color: black;">$1</strong>`);
    }
});
