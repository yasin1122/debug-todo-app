const API_URL = 'http://localhost:8080';
let currentUser = null;
let allTodos = [];
let filteredTodos = [];
let currentPage = 1;
let userPreferences = null;
let tableSettings = null;
let editingTodoId = null;

async function checkAuth() {
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('user_id');
    const username = localStorage.getItem('username');

    if (!token || !userId) {
        window.location.href = 'login.html';
        return false;
    }

    const response = await fetch(`${API_URL}/api/auth/verify`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token })
    });

    if (!response.ok) {
        localStorage.clear();
        window.location.href = 'login.html';
        return false;
    }

    currentUser = { id: userId, username, token };
    document.getElementById('username-display').textContent = `👤 ${username}`;
    return true;
}

async function loadPreferences() {
    const response = await fetch(`${API_URL}/preferences`, {
        headers: {
            'X-User-Id': currentUser.id
        }
    });

    if (response.ok) {
        const data = await response.json();
        userPreferences = data.preferences;
        tableSettings = data.table_settings;

        document.body.className = `${userPreferences.theme}-theme`;
        document.getElementById('theme-toggle').textContent = userPreferences.theme === 'dark' ? '☀️' : '🌙';
        document.getElementById('filter-status').value = userPreferences.filter_status;
        document.getElementById('sort-by').value = userPreferences.sort_by;
        document.getElementById('sort-order').value = userPreferences.sort_order;
        document.getElementById('items-per-page').value = userPreferences.items_per_page;

        applyColumnSettings();
    }
}

async function savePreferences(updates) {
    const data = {};

    if (updates.preferences) {
        data.preferences = { ...userPreferences, ...updates.preferences };
        userPreferences = data.preferences;
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

async function loadTodos() {
    const sortBy = document.getElementById('sort-by').value;
    const sortOrder = document.getElementById('sort-order').value;
    const filterStatus = document.getElementById('filter-status').value;

    const params = new URLSearchParams({
        status: filterStatus,
        sort_by: sortBy,
        sort_order: sortOrder
    });

    const response = await fetch(`${API_URL}/api/todos?${params}`, {
        headers: {
            'X-User-Id': currentUser.id
        }
    });

    if (response.ok) {
        allTodos = await response.json();

        filteredTodos = allTodos;

        renderTodos();
    }
}

function renderTodos() {
    const tbody = document.getElementById('todos-tbody');
    const emptyState = document.getElementById('empty-state');
    const itemsPerPage = parseInt(document.getElementById('items-per-page').value);

    updateSortIndicators();

    if (filteredTodos.length === 0) {
        tbody.innerHTML = '';
        emptyState.style.display = 'block';
        updatePagination(0, 0);
        return;
    }

    emptyState.style.display = 'none';

    const totalPages = Math.ceil(filteredTodos.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageTodos = filteredTodos.slice(startIndex, endIndex);

    tbody.innerHTML = pageTodos.map(todo => {
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
    }).join('');

    updatePagination(currentPage, totalPages);
    applyColumnSettings();
}

function updateSortIndicators() {
    const sortBy = document.getElementById('sort-by').value;
    const sortOrder = document.getElementById('sort-order').value;

    // Remove all sort classes first
    document.querySelectorAll('.sortable').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });

    // Add the appropriate class to the sorted column
    const sortedTh = document.querySelector(`th[data-column="${sortBy}"]`);
    if (sortedTh && sortedTh.classList.contains('sortable')) {
        sortedTh.classList.add(sortOrder === 'asc' ? 'sort-asc' : 'sort-desc');
    }
}

function updatePagination(page, totalPages) {
    document.getElementById('page-info').textContent = totalPages > 0 ? `Page ${page} of ${totalPages}` : 'No data';
    document.getElementById('prev-page').disabled = page <= 1;
    document.getElementById('next-page').disabled = page >= totalPages;
}

function applyColumnSettings() {
    if (!tableSettings || !tableSettings.visible_columns) return;

    const visibleColumns = typeof tableSettings.visible_columns === 'string'
        ? JSON.parse(tableSettings.visible_columns)
        : tableSettings.visible_columns;

    document.querySelectorAll('#todos-table [data-column]').forEach(el => {
        const column = el.getAttribute('data-column');
        el.style.display = visibleColumns.includes(column) || column === 'actions' ? '' : 'none';
    });
}

async function toggleComplete(todoId) {
    await fetch(`${API_URL}/api/todos/${todoId}/complete`, {
        method: 'PUT',
        headers: {
            'X-User-Id': currentUser.id
        }
    });
    await loadTodos();
}

async function deleteTodo(todoId) {
    if (!confirm('Are you sure you want to delete this todo?')) return;

    await fetch(`${API_URL}/api/todos/${todoId}`, {
        method: 'DELETE',
        headers: {
            'X-User-Id': currentUser.id
        }
    });
    await loadTodos();
}

async function editTodo(todoId) {
    const todo = allTodos.find(t => t.id === todoId);
    if (!todo) return;

    editingTodoId = todoId;
    document.getElementById('modal-title').textContent = 'Edit Todo';
    document.getElementById('todo-title').value = todo.title;
    document.getElementById('todo-description').value = todo.description || '';
    document.getElementById('todo-priority').value = todo.priority;

    if (todo.due_date) {
        const date = new Date(todo.due_date);
        const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
        document.getElementById('todo-due-date').value = localDate.toISOString().slice(0, 16);
    }

    showModal('todo-modal');
}

function showModal(modalId) {
    document.getElementById(modalId).style.display = 'flex';
}

function hideModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

document.addEventListener('DOMContentLoaded', async () => {
    if (!await checkAuth()) return;

    await loadPreferences();
    await loadTodos();

    document.getElementById('logout-btn').addEventListener('click', async () => {
        await fetch(`${API_URL}/api/auth/logout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: currentUser.token })
        });
        localStorage.clear();
        window.location.href = 'login.html';
    });

    document.getElementById('theme-toggle').addEventListener('click', async () => {
        const newTheme = userPreferences.theme === 'dark' ? 'light' : 'dark';
        document.body.className = `${newTheme}-theme`;
        document.getElementById('theme-toggle').textContent = newTheme === 'dark' ? '☀️' : '🌙';
        await savePreferences({ preferences: { theme: newTheme } });
    });

    document.getElementById('add-todo-btn').addEventListener('click', () => {
        editingTodoId = null;
        document.getElementById('modal-title').textContent = 'Add Todo';
        document.getElementById('todo-form').reset();
        showModal('todo-modal');
    });

    document.getElementById('refresh-btn').addEventListener('click', loadTodos);

    document.getElementById('filter-status').addEventListener('change', async (e) => {
        currentPage = 1;
        await savePreferences({ preferences: { filter_status: e.target.value } });
        await loadTodos();
    });

    document.getElementById('sort-by').addEventListener('change', async (e) => {
        currentPage = 1;
        await savePreferences({ preferences: { sort_by: e.target.value } });
        await loadTodos();
    });

    document.getElementById('sort-order').addEventListener('change', async (e) => {
        currentPage = 1;
        await savePreferences({ preferences: { sort_order: e.target.value } });
        await loadTodos();
    });

    document.getElementById('items-per-page').addEventListener('change', async (e) => {
        await savePreferences({ preferences: { items_per_page: parseInt(e.target.value) } });
        currentPage = 1;
        renderTodos();
    });

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

    document.getElementById('column-settings-btn').addEventListener('click', () => {
        const visibleColumns = typeof tableSettings.visible_columns === 'string'
            ? JSON.parse(tableSettings.visible_columns)
            : tableSettings.visible_columns || [];

        document.querySelectorAll('#column-settings-modal input[type="checkbox"]').forEach(checkbox => {
            const column = checkbox.getAttribute('data-column');
            checkbox.checked = visibleColumns.includes(column) || column === 'actions';
        });

        showModal('column-settings-modal');
    });

    document.getElementById('save-column-settings').addEventListener('click', async () => {
        const visibleColumns = [];
        document.querySelectorAll('#column-settings-modal input[type="checkbox"]:checked').forEach(checkbox => {
            visibleColumns.push(checkbox.getAttribute('data-column'));
        });

        await savePreferences({ table_settings: { visible_columns: visibleColumns } });
        applyColumnSettings();
        hideModal('column-settings-modal');
    });

    document.getElementById('todo-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const todoData = {
            title: document.getElementById('todo-title').value,
            description: document.getElementById('todo-description').value,
            priority: document.getElementById('todo-priority').value,
            due_date: document.getElementById('todo-due-date').value || null
        };

        if (editingTodoId) {
            await fetch(`${API_URL}/api/todos/${editingTodoId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-Id': currentUser.id
                },
                body: JSON.stringify(todoData)
            });
        } else {
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
        await loadTodos();
    });

    document.querySelectorAll('.modal-close, .modal-cancel').forEach(el => {
        el.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            if (modal) hideModal(modal.id);
        });
    });

    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) hideModal(modal.id);
        });
    });

    document.querySelectorAll('.sortable').forEach(th => {
        th.addEventListener('click', async () => {
            const column = th.getAttribute('data-column');
            const currentSort = document.getElementById('sort-by').value;
            const currentOrder = document.getElementById('sort-order').value;

            let newSort = currentSort;
            let newOrder;

            if (currentSort === column) {
                newOrder = currentOrder === 'desc' ? 'asc' : 'desc';
                document.getElementById('sort-order').value = newOrder;
            } else {
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