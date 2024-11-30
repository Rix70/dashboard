function createPage(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    // Добавляем порядок параметров
    formData.append('parameters_order', selectedParametersOrder.join(','));
    
    // Проверяем, выбран ли хотя бы один параметр
    if (selectedParametersOrder.length === 0) {
        showNotification('Выберите хотя бы один параметр!', 'error');
        return;
    }

    fetchWithCsrf('/create_page', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Страница успешно создана');
            setTimeout(() => {
                window.location.href = data.redirect_url;
            }, 1000);
        } else {
            showNotification(data.error || 'Произошла ошибка при создании страницы', 'error');
        }
    })
    .catch(error => {
        showNotification('Произошла ошибка при создании страницы', 'error');
    });
}
// Функции для управления страницами
function editPage(pageId) {
    document.querySelectorAll('.card-body').forEach(form => form.style.display = 'none');
    document.getElementById(`editForm${pageId}`).style.display = 'block';
    updateSelectedParameters(pageId);
}

function cancelEdit(pageId) {
    document.getElementById(`editForm${pageId}`).style.display = 'none';
}

function deletePage(pageId) {
    if (confirm('Вы уверены, что хотите удалить эту страницу и все её подстраницы?')) {
        fetchWithCsrf(`/delete_page/${pageId}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector(`[data-page-id="${pageId}"]`).remove();
                showNotification('Страница успешно удалена');
            } else {
                showNotification(data.error || 'Произошла ошибка при удалении страницы', 'error');
            }
        })
        .catch(error => {
            showNotification('Произошла ошибка при удалении страницы', 'error');
        });
    }
}

function updatePage(event, pageId) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    // Добавляем порядок параметров
    const parametersOrder = document.getElementById(`parameters_order${pageId}`).value;
    formData.append('parameters_order', parametersOrder);

    fetchWithCsrf(`/update_page/${pageId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Страница успешно обновлена');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(data.error || 'Произошла ошибка при обновлении страницы', 'error');
        }
    })
    .catch(error => {
        showNotification('Произошла ошибка при обновлении страницы', 'error');
    });
}

// Функции для фильтрации и отображения параметров
function filterParameters(pageId) {
    const searchText = document.querySelector(`${pageId === 'create' ? '.search-box' : `#editForm${pageId} .search-box`}`).value.toLowerCase();
    const items = document.querySelectorAll(`${pageId === 'create' ? '.parameter-item' : `#editForm${pageId} .parameter-item`}`);
    
    items.forEach(item => {
        const text = item.querySelector('.form-check-label').textContent.toLowerCase();
        item.style.display = text.includes(searchText) ? '' : 'none';
    });
}
// Глобальная переменная для хранения порядка параметров
let selectedParametersOrder = [];

// Функция для инициализации порядка параметров
function initializeParametersOrder(pageId) {
    const orderInput = document.getElementById(`parameters_order${pageId}`);
    if (orderInput && orderInput.value) {
        selectedParametersOrder = orderInput.value.split(',');
    }
}

function updateSelectedParameters(pageId) {
    const selectedTags = document.getElementById(`selectedTags${pageId}`);
    if (!selectedTags) return;
    
    // Инициализируем порядок при первом вызове
    if (selectedParametersOrder.length === 0) {
        initializeParametersOrder(pageId);
    }
    
    selectedTags.innerHTML = '';
    // Получаем все параметры в том порядке, в котором они отображаются в списке
    const parameterItems = document.querySelectorAll(`#editForm${pageId} input[name="selected_ids"]`);
    
    // Создаем временный массив для новых выбранных параметров
    let newSelectedOrder = [...selectedParametersOrder];
    
    // Обрабатываем каждый параметр
    parameterItems.forEach(checkbox => {
        if (checkbox.checked && !newSelectedOrder.includes(checkbox.value)) {
            // Добавляем новый выбранный параметр в конец списка
            newSelectedOrder.push(checkbox.value);
        } else if (!checkbox.checked && newSelectedOrder.includes(checkbox.value)) {
            // Удаляем параметр из списка, если он был снят
            newSelectedOrder = newSelectedOrder.filter(id => id !== checkbox.value);
        }
    });
    
    // Обновляем глобальный массив
    selectedParametersOrder = newSelectedOrder;
    
    // Отображаем параметры в сохраненном порядке
    selectedParametersOrder.forEach((paramId, index) => {
        const checkbox = document.querySelector(`#editForm${pageId} input[value="${paramId}"]`);
        if (checkbox && checkbox.checked) {
            const label = document.querySelector(`label[for="${checkbox.id}"]`).textContent;
            const tag = document.createElement('span');
            tag.className = 'parameter-tag';
            tag.textContent = `${index + 1}. ${label}`;
            selectedTags.appendChild(tag);
        }
    });

    // Обновляем скрытое поле с порядком параметров
    let orderInput = document.getElementById(`parameters_order${pageId}`);
    if (!orderInput) {
        orderInput = document.createElement('input');
        orderInput.type = 'hidden';
        orderInput.id = `parameters_order${pageId}`;
        orderInput.name = 'parameters_order';
        document.querySelector(`#editForm${pageId}`).appendChild(orderInput);
    }
    orderInput.value = selectedParametersOrder.join(',');

}

// Добавляем инициализацию при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.card-body');
    forms.forEach(form => {
        const pageId = form.id.replace('editForm', '');
        initializeParametersOrder(pageId);
    });
});

function updateCreatePageParameters() {
    const selectedTags = document.getElementById('selectedTags');
    if (!selectedTags) return;
    
    selectedTags.innerHTML = '';
    const parameterItems = document.querySelectorAll('input[name="selected_ids"]');
    
    // Обновляем список выбранных параметров
    parameterItems.forEach(checkbox => {
        if (checkbox.checked && !selectedParametersOrder.includes(checkbox.value)) {
            selectedParametersOrder.push(checkbox.value);
        } else if (!checkbox.checked && selectedParametersOrder.includes(checkbox.value)) {
            selectedParametersOrder = selectedParametersOrder.filter(id => id !== checkbox.value);
        }
    });
    
    // Отображаем параметры в порядке выбора
    selectedParametersOrder.forEach((paramId, index) => {
        const checkbox = document.querySelector(`input[value="${paramId}"]`);
        if (checkbox && checkbox.checked) {
            const label = document.querySelector(`label[for="${checkbox.id}"]`).textContent;
            const tag = document.createElement('span');
            tag.className = 'parameter-tag';
            tag.textContent = `${index + 1}. ${label}`;
            selectedTags.appendChild(tag);
        }
    });
    
    // Обновляем скрытое поле с порядком параметров
    let orderInput = document.getElementById('parameters_order');
    if (!orderInput) {
        orderInput = document.createElement('input');
        orderInput.type = '';   // hidden 
        orderInput.id = 'parameters_order';
        orderInput.name = 'parameters_order';
        document.querySelector('.create-page-form').appendChild(orderInput);
    }
    orderInput.value = selectedParametersOrder.join(',');
}

function toggleWeightParameter(select, paramId) {
    const weightParamDiv = document.getElementById(`weight_param_${paramId}`);
    if (select.value === 'weighted_avg') {
        weightParamDiv.style.display = 'block';
    } else {
        weightParamDiv.style.display = 'none';
    }
}

// При загрузке страницы проверяем все селекты
document.addEventListener('DOMContentLoaded', function() {
    const selects = document.querySelectorAll('.aggregation-type');
    selects.forEach(select => {
        const paramId = select.name.replace('aggregation_type_', '');
        toggleWeightParameter(select, paramId);
    });
});

function updateAggregation(event, paramId) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    formData.append('param_id', paramId);
    formData.append('csrf_token', document.querySelector('meta[name="csrf-token"]').content);
    
    fetchWithCsrf('/manage_aggregation', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Настройки успешно сохранены');
        } else {
            showNotification(data.error || 'Произошла ошибка', 'error');
        }
    })
    .catch(error => {
        showNotification('Произошла ошибка при сохранении', 'error');
    });
}


function toggleManualInput(checkbox, paramId) {
    const select = document.getElementById(`weight_select_${paramId}`);
    const manualInput = checkbox.closest('.manual-id-input').querySelector('.manual-weight-id');
    
    if (checkbox.checked) {
        select.disabled = true;
        manualInput.style.display = 'block';
    } else {
        select.disabled = false;
        manualInput.style.display = 'none';
        manualInput.value = '';
    }
}

// Обновляем функцию updateAggregation для обработки ручного ввода ID
function updateAggregation(event, paramId) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    // Проверяем, используется ли ручной ввод ID
    const manualCheckbox = form.querySelector('input[type="checkbox"]');
    if (manualCheckbox && manualCheckbox.checked) {
        const manualId = form.querySelector(`.manual-weight-id`).value;
        formData.set('weight_parameter_id', manualId);
    }
    
    formData.append('param_id', paramId);
    formData.append('csrf_token', document.querySelector('meta[name="csrf-token"]').content);
    
    fetchWithCsrf('/manage_aggregation', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Настройки успешно сохранены');
        } else {
            showNotification(data.error || 'Произошла ошибка', 'error');
        }
    })
    .catch(error => {
        showNotification('Произошла ошибка при сохранении', 'error');
    });
}

// Добавляем функцию для получения CSRF-токена
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').content;
}

// Обновляем все fetch запросы, добавляя CSRF-токен в заголовки
function fetchWithCsrf(url, options = {}) {
    const defaultHeaders = {
        'X-CSRFToken': getCsrfToken()
    };
    
    // Если передаем FormData, не устанавливаем Content-Type
    if (!(options.body instanceof FormData)) {
        defaultHeaders['Content-Type'] = 'application/json';
    }
    
    return fetch(url, {
        ...options,
        headers: {
            ...defaultHeaders,
            ...(options.headers || {})
        }
    });
}

// Функция для фильтрации параметров на странице управления агрегацией
function filterAggregationParameters() {
    const searchText = document.querySelector('#searchBox').value.toLowerCase();
    const cards = document.querySelectorAll('.parameter-card');
    
    cards.forEach(card => {
        const title = card.querySelector('h3').textContent.toLowerCase();
        const id = card.querySelector('.parameter-id').textContent.toLowerCase();
        const text = title + ' ' + id;
        
        if (text.includes(searchText)) {
            card.style.display = '';
            // Добавляем подсветку найденного текста если нужно
            card.classList.remove('not-found');
        } else {
            card.style.display = 'none';
            card.classList.add('not-found');
        }
    });
}

// Добавляем очистку поиска
function clearAggregationSearch() {
    const searchBox = document.querySelector('#searchBox');
    searchBox.value = '';
    filterAggregationParameters();
}

