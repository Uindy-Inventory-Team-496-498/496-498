let currentSortColumn = '';
let currentSortOrder = 'default';

function sortList(tableBodyId, column) {
    const tableBody = document.getElementById(tableBodyId);
    const rows = Array.from(tableBody.rows);

    if (currentSortColumn === column) {
        if (currentSortOrder === 'asc') {
            currentSortOrder = 'desc';
        } else if (currentSortOrder === 'desc') {
            currentSortOrder = 'default';
        } else {
            currentSortOrder = 'asc';
        }
    } else {
        currentSortColumn = column;
        currentSortOrder = 'asc';
    }

    if (currentSortOrder === 'default') {
        rows.sort((a, b) => parseInt(a.cells[0].textContent) - parseInt(b.cells[0].textContent)); // Default sort by ID
    } else {
        rows.sort((a, b) => {
            const aValue = getSortValue(a, column);
            const bValue = getSortValue(b, column);

            if (currentSortOrder === 'asc') {
                return aValue.localeCompare(bValue, undefined, { numeric: true });
            } else {
                return bValue.localeCompare(aValue, undefined, { numeric: true });
            }
        });
    }

    tableBody.innerHTML = '';

    rows.forEach(row => tableBody.appendChild(row));

    updateSortArrows(column, currentSortOrder);
}

function getSortValue(row, column) {
    const cell = row.querySelector(`.column-${column}`);
    return cell ? cell.textContent.trim() : '';
}

function updateSortArrows(column, order) {
    const columns = ['id', 'material', 'name', 'room', 'cabinet', 'shelf', 'amount', 'unit', 'concentration', 'sds', 'notes', 'instrument', 'checked-out-by', 'checked-out-date', 'expected', 'percentage'];
    columns.forEach(col => {
        const arrow = document.getElementById(`sort-arrow-${col}`);
        if (arrow) {
            if (col === column) {
                if (order === 'asc') {
                    arrow.textContent = '▲';
                } else if (order === 'desc') {
                    arrow.textContent = '▼';
                } else {
                    arrow.textContent = '';
                }
            } else {
                arrow.textContent = '';
            }
        }
    });
}

function filterList() {
    const selectedTypes = Array.from(document.querySelectorAll('.type-choice:checked')).map(cb => cb.value);
    const selectedLocations = Array.from(document.querySelectorAll('.location-choice:checked')).map(cb => cb.value);
    const selectedSDS = Array.from(document.querySelectorAll('.sds-choice:checked')).map(cb => cb.value);
    const rows = document.querySelectorAll('.chemical-row');

    rows.forEach(row => {
        const rowType = row.getAttribute('data-type');
        const rowLocation = row.getAttribute('data-location');
        let rowSDS = row.getAttribute('data-sds');
        if (rowSDS === '') rowSDS = 'none';

        const typeMatches = selectedTypes.length === 0 || selectedTypes.includes(rowType);
        const locationMatches = selectedLocations.length === 0 || selectedLocations.includes(rowLocation);
        const sdsMatches = selectedSDS.length === 0 || selectedSDS.includes(rowSDS);

        if (typeMatches && locationMatches && sdsMatches) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });

    updateSelectAllCheckbox('type');
    updateSelectAllCheckbox('location');
    updateSelectAllCheckbox('sds');
}

function toggleColumn(checkbox) {
    const columnClass = `column-${checkbox.value}`;
    const cells = document.querySelectorAll(`.${columnClass}`);
    cells.forEach(cell => {
        cell.style.display = checkbox.checked ? '' : 'none';
    });
}

function selectAll(category) {
    const selectAllCheckbox = document.getElementById(`select-all-${category}`);
    const checkboxes = document.querySelectorAll(`.${category}-choice`);
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
    filterList();
    updateSelectAllCheckbox(category);
}

function updateSelectAllCheckbox(category) {
    const checkboxes = document.querySelectorAll(`.${category}-choice`);
    const selectAllCheckbox = document.getElementById(`select-all-${category}`);
    const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);
    const allUnchecked = Array.from(checkboxes).every(checkbox => !checkbox.checked);
    selectAllCheckbox.checked = allChecked;
    selectAllCheckbox.indeterminate = !allChecked && !allUnchecked;
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.type-choice, .location-choice, .sds-choice').forEach(checkbox => {
        checkbox.checked = true;
        checkbox.addEventListener('change', () => {
            filterList();
            updateSelectAllCheckbox(checkbox.classList[0].split('-')[0]);
        });
    });
    document.querySelectorAll('.select-all').forEach(checkbox => {
        checkbox.addEventListener('change', () => selectAll(checkbox.getAttribute('data-category')));
    });
    filterList();
});
