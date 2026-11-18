(function () {
    const pageSize = 10;
    const excludedTableSelectors = ['#abonoTable'];
    const states = [];

    function isPlaceholder(row) {
        const firstCell = row.cells[0];
        return row.dataset.paginationIgnore === 'true' ||
            row.id.startsWith('no-') ||
            row.hasAttribute('data-pagination-summary') ||
            (row.cells.length === 1 && firstCell && firstCell.colSpan > 1);
    }

    function makePagination(items, mount, label, isFiltered) {
        if (mount.dataset.paginationInitialized === 'true') return;
        mount.dataset.paginationInitialized = 'true';

        const container = document.createElement('div');
        container.className = 'system-pagination d-flex justify-content-between align-items-center flex-wrap gap-2 mt-3';
        container.hidden = true;
        const info = document.createElement('small');
        info.className = 'text-muted';
        info.setAttribute('aria-live', 'polite');
        const nav = document.createElement('nav');
        nav.setAttribute('aria-label', `Paginación de ${label}`);
        const pages = document.createElement('ul');
        pages.className = 'pagination pagination-sm mb-0';
        nav.appendChild(pages);
        container.append(info, nav);
        mount.insertAdjacentElement('afterend', container);

        const state = { items, mount, label, isFiltered, container, info, pages, currentPage: 1 };
        states.push(state);

        function addPage(text, page, disabled, active, ariaLabel) {
            const item = document.createElement('li');
            item.className = `page-item${disabled ? ' disabled' : ''}${active ? ' active' : ''}`;
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'page-link';
            button.textContent = text;
            button.disabled = disabled;
            button.setAttribute('aria-label', ariaLabel);
            if (active) button.setAttribute('aria-current', 'page');
            button.addEventListener('click', () => {
                state.currentPage = page;
                render(state);
            });
            item.appendChild(button);
            pages.appendChild(item);
        }

        function renderControls(totalPages) {
            pages.replaceChildren();
            if (totalPages <= 1) return;

            addPage('‹', state.currentPage - 1, state.currentPage === 1, false, 'Página anterior');
            let firstPage = Math.max(1, state.currentPage - 2);
            let lastPage = Math.min(totalPages, firstPage + 4);
            firstPage = Math.max(1, lastPage - 4);
            if (firstPage > 1) {
                addPage('1', 1, false, false, 'Página 1');
                if (firstPage > 2) addGap();
            }
            for (let page = firstPage; page <= lastPage; page += 1) {
                if (page === 1 && firstPage > 1) continue;
                addPage(String(page), page, false, page === state.currentPage, `Página ${page}`);
            }
            if (lastPage < totalPages) {
                if (lastPage < totalPages - 1) addGap();
                addPage(String(totalPages), totalPages, false, false, `Página ${totalPages}`);
            }
            addPage('›', state.currentPage + 1, state.currentPage === totalPages, false, 'Página siguiente');

            function addGap() {
                const gap = document.createElement('li');
                gap.className = 'page-item disabled';
                gap.innerHTML = '<span class="page-link" aria-hidden="true">…</span>';
                pages.appendChild(gap);
            }
        }

        state.renderControls = renderControls;
        render(state);
    }

    function render(state) {
        const eligible = state.items.filter(item => !state.isFiltered(item));
        const totalPages = Math.max(1, Math.ceil(eligible.length / pageSize));
        if (state.currentPage > totalPages) state.currentPage = totalPages;
        const start = (state.currentPage - 1) * pageSize;
        const visible = new Set(eligible.slice(start, start + pageSize));

        state.items.forEach(item => item.classList.toggle('system-page-hidden', !visible.has(item)));
        state.container.hidden = totalPages <= 1;
        const first = eligible.length ? start + 1 : 0;
        const last = Math.min(start + pageSize, eligible.length);
        state.info.textContent = `Mostrando ${first}–${last} de ${eligible.length} ${state.label}`;
        state.renderControls(totalPages);
    }

    function init() {
        document.querySelectorAll('table').forEach(table => {
            if (table.closest('.modal') || excludedTableSelectors.some(selector => table.matches(selector)) || table.dataset.pagination === 'off') return;
            const body = table.tBodies[0];
            if (!body || body.id === 'emergenciasTableBody' || body.id === 'abonoTableBody') return;
            const items = Array.from(body.rows).filter(row => !isPlaceholder(row));
            if (items.length <= pageSize) return;
            const mount = table.closest('.table-responsive') || table;
            makePagination(items, mount, body.dataset.paginationLabel || table.dataset.paginationLabel || 'registros', row => row.style.display === 'none' || row.classList.contains('d-none'));
        });

        document.querySelectorAll('[data-pagination-list]').forEach(list => {
            const items = Array.from(list.querySelectorAll(':scope > [data-pagination-item]'));
            if (items.length <= pageSize) return;
            makePagination(items, list, list.dataset.paginationLabel || 'registros', item => item.style.display === 'none' || item.classList.contains('d-none'));
        });
    }

    document.addEventListener('DOMContentLoaded', () => window.setTimeout(init, 0));
    ['input', 'change', 'keyup'].forEach(eventName => {
        document.addEventListener(eventName, event => {
            if (!event.target.closest('input, select, textarea')) return;
            refreshAfterFilter();
        });
    });

    document.addEventListener('click', event => {
        if (event.target.closest('#cursoFilterButton, #activityFilterButton')) refreshAfterFilter();
    });

    function refreshAfterFilter() {
        window.setTimeout(() => states.forEach(state => {
            state.currentPage = 1;
            render(state);
        }), 0);
    }
})();
