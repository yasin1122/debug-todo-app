// ============================================================
// app.js — all frontend logic for the todo app
//
// How the frontend works at a high level:
//   1. On page load, check if the user is logged in (checkAuth).
//   2. Load their saved preferences (theme, sort order, etc.).
//   3. Fetch and render their todos.
//   4. Wire up all the buttons, dropdowns, and modals to event listeners.
//
// All communication with the server goes through fetch() calls to the
// proxy at http://localhost:8080. The proxy handles routing from there.
// ============================================================

const API_URL = 'http://localhost:8080'; // The single address the browser talks to

// ---- Global state -------------------------------------------------------
// These variables are declared outside functions so every function can
// read and update them. Think of them as the app's shared memory.

let currentUser = null;       // The logged-in user: { id, username, token }
let allTodos = [];            // All todos returned by the last fetch
let filteredTodos = [];       // The subset of todos after applying the current filter
let currentPage = 1;          // Which page of results is currently showing
let userPreferences = null;   // Theme, sort order, filter, items per page, etc.
let tableSettings = null;     // Which table columns are currently visible
let editingTodoId = null;     // If we're editing a todo, this holds its ID; null = adding new


// ============================================================
// AUTH
// ============================================================

async function checkAuth() {
    // Called on every page load. Reads the token from localStorage (saved at
    // login) and asks the server whether it's still valid.
    // If there's no token, or it's expired, redirect to the login page.
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('user_id');
    const username = localStorage.getItem('username');

    if (!token || !userId) {
        // No credentials stored — definitely not logged in.
        window.location.href = 'login.html';
        return false;
    }

    // Ask the server to verify the token (it checks expiry and existence).
    const response = await fetch(`${API_URL}/api/auth/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
    });

    if (!response.ok) {
        // Token invalid or expired — clear stale data and redirect.
        localStorage.clear();
        window.location.href = 'login.html';
        return false;
    }

    // Auth confirmed — populate the global currentUser object and show the
    // username in the header.
    currentUser = { id: userId, username, token };
    document.getElementById('username-display').textContent = `👤 ${username}`;
    return true;
}


// ============================================================
// PREFERENCES
// ============================================================

async function loadPreferences() {
    // Fetch the user's saved preferences from the proxy (which reads
    // preferences.db and returns both objects in one response).
    const response = await fetch(`${API_URL}/preferences`, {
        headers: { 'X-User-Id': currentUser.id }
    });

    if (response.ok) {
        const data = await response.json();
        userPreferences = data.preferences;     // Theme, sort, filter, etc.
        tableSettings = data.table_settings;    // Which columns are visible

        // Apply the saved preferences to the UI immediately.
        document.body.className = `${userPreferences.theme}-theme`;
        document.getElementById('theme-toggle').textContent = userPreferences.theme === 'dark' ? '☀️' : '🌙';
        document.getElementById('filter-status').value = userPreferences.filter_status;
        document.getElementById('sort-by').value = userPreferences.sort_by;
        document.getElementById('sort-order').value = userPreferences.sort_order;
        document.getElementById('items-per-page').value = userPreferences.items_per_page;

        // Show/hide columns based on saved table settings.
        applyColumnSettings();
    }
}

async function savePreferences(updates) {
    // Merge the incoming updates with the current in-memory preferences,
    // then POST the merged result to the proxy so it's persisted in the DB.
    //
    // `updates` can contain `preferences`, `table_settings`, or both.
    // Example: savePreferences({ preferences: { theme: 'dark' } })

    const data = {};

    if (updates.preferences) {
        // Merge: spread the existing prefs first, then overwrite with the new values.
        data.preferences = { ...userPreferences, ...updates.preferences };
        userPreferences = data.preferences; // Keep local state in sync
    }

    if (updates.table_settings) {
        data.table_settings = { ...tableSettings, ...updates.table_settings };
        tableSettings = data.table_settings;
    }

    await fetch(`${API_URL}/preferences`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-User-Id': currentUser.id
        },
        body: JSON.stringify(data)
    });
}


// ============================================================
// TODOS — FETCHING
// ============================================================

async function loadTodos() {
    // Read the current filter/sort values from the dropdowns, send them as
    // query parameters, and replace allTodos + filteredTodos with the result.
    const sortBy = document.getElementById('sort-by').value;
    const sortOrder = document.getElementById('sort-order').value;
    const filterStatus = document.getElementById('filter-status').value;

    // URLSearchParams builds a query string like "?status=active&sort_by=title&sort_order=asc"
    const params = new URLSearchParams({
        status: filterStatus,
        sort_by: sortBy,
        sort_order: sortOrder
    });

    const response = await fetch(`${API_URL}/api/todos?${params}`, {
        headers: { 'X-User-Id': currentUser.id }
    });

    if (response.ok) {
        allTodos = await response.json(); // Parse the JSON array from the response body
        filteredTodos = allTodos;         // No client-side filtering — server already filtered
        renderTodos();
    }
}


// ============================================================
// TODOS — RENDERING
// ============================================================

function renderTodos() {
    // Build the visible table rows for the current page and inject them into the DOM.
    const tbody = document.getElementById('todos-tbody');
    const emptyState = document.getElementById('empty-state');
    const itemsPerPage = parseInt(document.getElementById('items-per-page').value);

    // Refresh the ↑/↓ sort arrow on the active column header.
    updateSortIndicators();

    if (filteredTodos.length === 0) {
        // No todos to show — display the empty state message instead.
        tbody.innerHTML = '';
        emptyState.style.display = 'block';
        updatePagination(0, 0);
        return;
    }

    emptyState.style.display = 'none';

    // Pagination: slice the full array to get only the current page's todos.
    const totalPages = Math.ceil(filteredTodos.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageTodos = filteredTodos.slice(startIndex, endIndex);

    // Build one <tr> per todo using a template string, then join them all into
    // one string and set it as the table body's inner HTML.
    tbody.innerHTML = pageTodos.map(todo => {
        // A todo is overdue if it has a due date, that date is in the past,
        // and the todo hasn't been completed yet.
        const isOverdue = todo.due_date && new Date(todo.due_date) < new Date() && todo.is_completed !== 1;
        const formattedDate = todo.due_date ? new Date(todo.due_date).toLocaleDateString() : '-';

        return `
            <tr data-todo-id="${todo.id}">
                <td data-column="title">${escapeHtml(todo.title)}</td>
                <td data-column="priority">
                    <span class="priority-${todo.priority}">${capitalizeFirst(todo.priority)}</span>
                </td>
                <td data-column="due_date" class="${isOverdue ? 'overdue' : ''}">${formattedDate}</td>
                <td data-column="completed">
                    <button class="todo-complete ${todo.is_completed === 1 ? 'completed' : ''}" onclick="toggleComplete(${todo.id})">
                        ${todo.is_completed === 1 ? '✓' : '○'}
                    </button>
                </td>
                <td data-column="actions" class="todo-actions">
                    <button class="action-btn" onclick="editTodo(${todo.id})">✏️</button>
                    <button class="action-btn" onclick="deleteTodo(${todo.id})">🗑️</button>
                </td>
            </tr>
        `;
    }).join(''); // join('') removes the commas between array items

    updatePagination(currentPage, totalPages);

    // Re-apply column visibility after rebuilding the table (new rows don't
    // inherit the previous display:none settings).
    applyColumnSettings();
}

function updateSortIndicators() {
    // Show an ↑ or ↓ arrow on whichever column is currently being sorted.
    const sortBy = document.getElementById('sort-by').value;
    const sortOrder = document.getElementById('sort-order').value;

    // First remove all arrows from every sortable header.
    document.querySelectorAll('.sortable').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });

    // Then add the correct arrow to the active column.
    const sortedTh = document.querySelector(`th[data-column="${sortBy}"]`);
    if (sortedTh && sortedTh.classList.contains('sortable')) {
        sortedTh.classList.add(sortOrder === 'asc' ? 'sort-asc' : 'sort-desc');
    }
}

function updatePagination(page, totalPages) {
    // Update the "Page X of Y" text and enable/disable the Prev/Next buttons.
    document.getElementById('page-info').textContent = totalPages > 0 ? `Page ${page} of ${totalPages}` : 'No data';
    document.getElementById('prev-page').disabled = page <= 1;
    document.getElementById('next-page').disabled = page >= totalPages;
}

function applyColumnSettings() {
    // Show or hide each table column based on the user's saved table settings.
    // We only touch elements inside #todos-table to avoid accidentally hiding
    // the checkboxes inside the column settings modal (which also use data-column).
    if (!tableSettings || !tableSettings.visible_columns) return;

    // visible_columns is stored as a JSON string in the DB; parse it if needed.
    const visibleColumns = typeof tableSettings.visible_columns === 'string'
        ? JSON.parse(tableSettings.visible_columns)
        : tableSettings.visible_columns;

    document.querySelectorAll('#todos-table [data-column]').forEach(el => {
        const column = el.getAttribute('data-column');
        // Actions column is always visible — users need it to edit/delete todos.
        el.style.display = visibleColumns.includes(column) || column === 'actions' ? '' : 'none';
    });
}


// ============================================================
// TODOS — MUTATIONS
// ============================================================

async function toggleComplete(todoId) {
    // Send a PUT request to flip this todo's is_completed flag, then reload.
    await fetch(`${API_URL}/api/todos/${todoId}/complete`, {
        method: 'PUT',
        headers: { 'X-User-Id': currentUser.id }
    });
    await loadTodos();
}

async function deleteTodo(todoId) {
    // Ask for confirmation before deleting — deletions are permanent.
    if (!confirm('Are you sure you want to delete this todo?')) return;

    await fetch(`${API_URL}/api/todos/${todoId}`, {
        method: 'DELETE',
        headers: { 'X-User-Id': currentUser.id }
    });
    await loadTodos();
}

async function editTodo(todoId) {
    // Pre-fill the Add/Edit modal with this todo's current values and open it.
    const todo = allTodos.find(t => t.id === todoId); // Look up the todo in memory
    if (!todo) return;

    editingTodoId = todoId; // Tell the form submit handler we're editing, not creating
    document.getElementById('modal-title').textContent = 'Edit Todo';
    document.getElementById('todo-title').value = todo.title;
    document.getElementById('todo-description').value = todo.description || '';
    document.getElementById('todo-priority').value = todo.priority;

    if (todo.due_date) {
        // datetime-local inputs expect the format "YYYY-MM-DDTHH:MM" in local time.
        // The date from the server is UTC, so we subtract the timezone offset to
        // convert it to the user's local time before displaying it.
        const date = new Date(todo.due_date);
        const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
        document.getElementById('todo-due-date').value = localDate.toISOString().slice(0, 16);
    }

    showModal('todo-modal');
}


// ============================================================
// MODAL HELPERS
// ============================================================

function showModal(modalId) {
    // Make the modal visible by changing its CSS display property.
    document.getElementById(modalId).style.display = 'flex';
}

function hideModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}


// ============================================================
// UTILITY HELPERS
// ============================================================

function escapeHtml(text) {
    // Prevent XSS (Cross-Site Scripting) attacks.
    // If a todo title contained <script>alert('hacked')</script>, inserting it
    // directly into innerHTML would execute the script. By setting textContent
    // instead, the browser escapes the special characters to harmless text.
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML; // Now safe to inject into innerHTML
}

function capitalizeFirst(str) {
    // 'medium' → 'Medium'
    return str.charAt(0).toUpperCase() + str.slice(1);
}


// ============================================================
// INITIALISATION — runs once when the page finishes loading
// ============================================================

document.addEventListener('DOMContentLoaded', async () => {
    // DOMContentLoaded fires when the HTML has been parsed and all elements
    // are accessible. We use async so we can await promises inside.

    // Redirect to login if not authenticated.
    if (!await checkAuth()) return;

    // Load preferences (theme, sort, filter) before fetching todos so the
    // UI is already configured when the data arrives.
    await loadPreferences();
    await loadTodos();

    // ---- Logout ----------------------------------------------------------
    document.getElementById('logout-btn').addEventListener('click', async () => {
        // Tell the server to invalidate the session, then clear local storage
        // and go back to the login page.
        await fetch(`${API_URL}/api/auth/logout`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: currentUser.token })
        });
        localStorage.clear();
        window.location.href = 'login.html';
    });

    // ---- Theme toggle ----------------------------------------------------
    document.getElementById('theme-toggle').addEventListener('click', async () => {
        const newTheme = userPreferences.theme === 'dark' ? 'light' : 'dark';
        // Update the CSS class on <body> immediately so the switch feels instant.
        document.body.className = `${newTheme}-theme`;
        document.getElementById('theme-toggle').textContent = newTheme === 'dark' ? '☀️' : '🌙';
        // Persist the new theme so it's remembered on next load.
        await savePreferences({ preferences: { theme: newTheme } });
    });

    // ---- Add todo button -------------------------------------------------
    document.getElementById('add-todo-btn').addEventListener('click', () => {
        editingTodoId = null; // null means "we're creating a new todo"
        document.getElementById('modal-title').textContent = 'Add Todo';
        document.getElementById('todo-form').reset(); // Clear any leftover values
        showModal('todo-modal');
    });

    // ---- Refresh button --------------------------------------------------
    document.getElementById('refresh-btn').addEventListener('click', loadTodos);

    // ---- Filter dropdown -------------------------------------------------
    document.getElementById('filter-status').addEventListener('change', async (e) => {
        currentPage = 1; // Reset to page 1 so you don't land on a non-existent page
        await savePreferences({ preferences: { filter_status: e.target.value } });
        await loadTodos();
    });

    // ---- Sort-by dropdown ------------------------------------------------
    document.getElementById('sort-by').addEventListener('change', async (e) => {
        currentPage = 1;
        await savePreferences({ preferences: { sort_by: e.target.value } });
        await loadTodos();
    });

    // ---- Sort-order dropdown ---------------------------------------------
    document.getElementById('sort-order').addEventListener('change', async (e) => {
        currentPage = 1;
        await savePreferences({ preferences: { sort_order: e.target.value } });
        await loadTodos();
    });

    // ---- Items-per-page dropdown -----------------------------------------
    document.getElementById('items-per-page').addEventListener('change', async (e) => {
        await savePreferences({ preferences: { items_per_page: parseInt(e.target.value) } });
        currentPage = 1;
        renderTodos(); // Re-render with existing data — no need to re-fetch
    });

    // ---- Pagination buttons ----------------------------------------------
    document.getElementById('prev-page').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderTodos();
        }
    });

    document.getElementById('next-page').addEventListener('click', () => {
        const itemsPerPage = parseInt(document.getElementById('items-per-page').value);
        const totalPages = Math.ceil(filteredTodos.length / itemsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            renderTodos();
        }
    });

    // ---- Column settings button ------------------------------------------
    document.getElementById('column-settings-btn').addEventListener('click', () => {
        // Before opening the modal, pre-check the checkboxes to match the
        // currently visible columns.
        const visibleColumns = typeof tableSettings.visible_columns === 'string'
            ? JSON.parse(tableSettings.visible_columns)
            : tableSettings.visible_columns || [];

        document.querySelectorAll('#column-settings-modal input[type="checkbox"]').forEach(checkbox => {
            const column = checkbox.getAttribute('data-column');
            checkbox.checked = visibleColumns.includes(column) || column === 'actions';
        });

        showModal('column-settings-modal');
    });

    // ---- Save column settings --------------------------------------------
    document.getElementById('save-column-settings').addEventListener('click', async () => {
        // Collect the names of all checked columns and save them.
        const visibleColumns = [];
        document.querySelectorAll('#column-settings-modal input[type="checkbox"]:checked').forEach(checkbox => {
            visibleColumns.push(checkbox.getAttribute('data-column'));
        });

        await savePreferences({ table_settings: { visible_columns: visibleColumns } });
        applyColumnSettings();
        hideModal('column-settings-modal');
    });

    // ---- Todo form submit (create or update) -----------------------------
    document.getElementById('todo-form').addEventListener('submit', async (e) => {
        e.preventDefault(); // Stop the browser from doing a full page reload

        const todoData = {
            title: document.getElementById('todo-title').value,
            description: document.getElementById('todo-description').value,
            priority: document.getElementById('todo-priority').value,
            due_date: document.getElementById('todo-due-date').value || null // null if empty
        };

        if (editingTodoId) {
            // editingTodoId is set — we're updating an existing todo.
            await fetch(`${API_URL}/api/todos/${editingTodoId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-Id': currentUser.id
                },
                body: JSON.stringify(todoData)
            });
        } else {
            // editingTodoId is null — we're creating a new todo.
            await fetch(`${API_URL}/api/todos`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-Id': currentUser.id
                },
                body: JSON.stringify(todoData)
            });
        }

        hideModal('todo-modal');
        await loadTodos(); // Refresh the list so the new/updated todo appears
    });

    // ---- Close modals (× button and Cancel button) -----------------------
    document.querySelectorAll('.modal-close, .modal-cancel').forEach(el => {
        el.addEventListener('click', (e) => {
            // Walk up the DOM from the clicked element until we find the modal.
            const modal = e.target.closest('.modal');
            if (modal) hideModal(modal.id);
        });
    });

    // ---- Close modals by clicking the dark backdrop ----------------------
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            // e.target is the exact element clicked. If it's the modal backdrop
            // (not a child element inside it), close the modal.
            if (e.target === modal) hideModal(modal.id);
        });
    });

    // ---- Clickable column headers ----------------------------------------
    // Clicking a sortable <th> changes the sort column (or toggles asc/desc
    // if the same column is clicked again). The new sort is persisted so it
    // survives a page refresh.
    document.querySelectorAll('.sortable').forEach(th => {
        th.addEventListener('click', async () => {
            const column = th.getAttribute('data-column');
            const currentSort = document.getElementById('sort-by').value;
            const currentOrder = document.getElementById('sort-order').value;

            let newSort = currentSort;
            let newOrder;

            if (currentSort === column) {
                // Same column clicked again — flip the direction.
                newOrder = currentOrder === 'desc' ? 'asc' : 'desc';
                document.getElementById('sort-order').value = newOrder;
            } else {
                // Different column — switch to it and default to descending.
                newSort = column;
                newOrder = 'desc';
                document.getElementById('sort-by').value = newSort;
                document.getElementById('sort-order').value = newOrder;
            }

            currentPage = 1;
            await savePreferences({ preferences: { sort_by: newSort, sort_order: newOrder } });
            await loadTodos();
        });
    });
});
