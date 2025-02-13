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
    switch (column) {
        case 'id':
            return row.cells[0].textContent;
        case 'material':
            return row.cells[1].textContent;
        case 'name':
            return row.cells[2].textContent;
        case 'room':
            return row.cells[3].textContent;
        case 'cabinet':
            return row.cells[4].textContent;
        case 'shelf':
            return row.cells[5].textContent;
        case 'amount':
            return row.cells[6].textContent;
        case 'unit':
            return row.cells[7].textContent;
        case 'concentration':
            return row.cells[8].textContent;
        case 'sds':
            return row.cells[9].textContent;
        case 'notes':
            return row.cells[10].textContent;
        case 'instrument':
            return row.cells[11].textContent;
        case 'checked-out-by':
            return row.cells[12].textContent;
        case 'checked-out-date':
            return row.cells[13].textContent;
        default:
            return '';
    }
}

function updateSortArrows(column, order) {
    const columns = ['id', 'material', 'name', 'room', 'cabinet', 'shelf', 'amount', 'unit', 'concentration', 'sds', 'notes', 'instrument', 'checked-out-by', 'checked-out-date'];
    columns.forEach(col => {
        const arrow = document.getElementById(`sort-arrow-${col}`);
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
    });
}

function toggleTriState(checkbox) {
    if (checkbox.readOnly) {
        checkbox.checked = checkbox.readOnly = false;
    } else if (!checkbox.checked) {
        checkbox.readOnly = checkbox.indeterminate = true;
    } else if (checkbox.checked) {
        checkbox.readOnly = checkbox.indeterminate = false;
    }
    filterList();
}

function filterList() {
    const selectedTypes = Array.from(document.querySelectorAll('.type-choice')).map(cb => ({
        value: cb.value,
        state: cb.indeterminate ? 'exclude' : (cb.checked ? 'include' : 'none')
    }));
    const selectedLocations = Array.from(document.querySelectorAll('.location-choice')).map(cb => ({
        value: cb.value,
        state: cb.indeterminate ? 'exclude' : (cb.checked ? 'include' : 'none')
    }));
    const selectedSDS = Array.from(document.querySelectorAll('.sds-choice')).map(cb => ({
        value: cb.value,
        state: cb.indeterminate ? 'exclude' : (cb.checked ? 'include' : 'none')
    }));
    const rows = document.querySelectorAll('.chemical-row');

    rows.forEach(row => {
        const rowType = row.getAttribute('data-type');
        const rowLocation = row.getAttribute('data-location');
        const rowSDS = row.getAttribute('data-sds');

        const typeMatches = selectedTypes.every(type => {
            if (type.state === 'none') return true;
            if (type.state === 'include') return rowType === type.value;
            if (type.state === 'exclude') return rowType !== type.value;
        });

        const locationMatches = selectedLocations.every(location => {
            if (location.state === 'none') return true;
            if (location.state === 'include') return rowLocation === location.value || rowLocation === '' || rowLocation === 'none';
            if (location.state === 'exclude') return rowLocation !== location.value && rowLocation !== '' && rowLocation !== 'none';
        });

        const sdsMatches = selectedSDS.every(sds => {
            if (sds.state === 'none') return true;
            if (sds.state === 'include') return rowSDS === sds.value || rowSDS === '' || rowSDS === 'none';
            if (sds.state === 'exclude') return rowSDS !== sds.value && rowSDS !== '' && rowSDS !== 'none';
        });

        if (typeMatches && locationMatches && sdsMatches) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function toggleColumn(checkbox) {
    const columnClass = `column-${checkbox.value}`;
    const cells = document.querySelectorAll(`.${columnClass}`);
    cells.forEach(cell => {
        cell.style.display = checkbox.checked ? '' : 'none';
    });
}
