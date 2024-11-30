// скрытие и отображение сайдбара
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const isMobile = window.innerWidth <= 768;

    // Функция для сохранения состояния сайдбара
    function saveSidebarState(isHidden) {
        localStorage.setItem('sidebarHidden', isHidden);
    }

    // Функция для загрузки состояния сайдбара
    function loadSidebarState() {
        return localStorage.getItem('sidebarHidden') === 'true';
    }

    // Функция переключения сайдбара
    function toggleSidebar() {
        if (isMobile) {
            sidebar.classList.toggle('sidebar-visible');
            sidebarOverlay.classList.toggle('active');
        } else {
            const isHidden = sidebar.classList.toggle('sidebar-hidden');
            mainContent.classList.toggle('main-content-expanded');
            saveSidebarState(isHidden);
        }
    }

    // Инициализация состояния сайдбара
    if (!isMobile && loadSidebarState()) {
        sidebar.classList.add('sidebar-hidden');
        mainContent.classList.add('main-content-expanded');
    }

    // Обработчики событий
    sidebarToggle.addEventListener('click', toggleSidebar);
    
    sidebarOverlay.addEventListener('click', function() {
        if (isMobile) {
            sidebar.classList.remove('sidebar-visible');
            sidebarOverlay.classList.remove('active');
        }
    });

    // Обработчик изменения размера окна
    window.addEventListener('resize', function() {
        const newIsMobile = window.innerWidth <= 768;
        if (newIsMobile !== isMobile) {
            location.reload();
        }
    });

    // Инициализация активной вкладки
    const activeTabId = document.querySelector('.nav-link.active').getAttribute('id');
    const tabName = activeTabId.replace('-tab', '');
    showTab(tabName);
});

// Функции для работы с вкладками
function showTab(tabName) {
    // Находим все вкладки и их содержимое
    const tabLinks = document.querySelectorAll('.nav-link');
    const tabContents = document.querySelectorAll('.tab-pane');
    
    // Убираем активный класс у всех вкладок
    tabLinks.forEach(tab => {
        tab.classList.remove('active');
        tab.setAttribute('aria-selected', 'false');
    });
    
    // Убираем активный класс у всего содержимого
    tabContents.forEach(content => {
        content.classList.remove('show', 'active');
    });
    
    // Активируем нужную вкладку
    const activeTab = document.getElementById(`${tabName}-tab`);
    activeTab.classList.add('active');
    activeTab.setAttribute('aria-selected', 'true');
    
    // Показываем содержимое активной вкладки
    const activeContent = document.getElementById(`${tabName}Tab`);
    activeContent.classList.add('show', 'active');
}

// Функция для показа уведомлений
function showNotification(message, type = 'success') {
    // Создаем контейнер для уведомлений, если его нет
    let container = document.querySelector('.notifications-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'notifications-container';
        document.body.appendChild(container);
    }

    // Создаем уведомление
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    // Добавляем сообщение
    const messageSpan = document.createElement('span');
    messageSpan.textContent = message;
    notification.appendChild(messageSpan);
    
    // Добавляем кнопку закрытия
    const closeButton = document.createElement('button');
    closeButton.className = 'notification-close';
    closeButton.innerHTML = '×';
    closeButton.onclick = () => removeNotification(notification);
    notification.appendChild(closeButton);
    
    // Добавляем уведомление в контейнер
    container.appendChild(notification);
    
    // Автоматически удаляем через 5 секунд
    setTimeout(() => {
        if (notification.parentElement) {
            removeNotification(notification);
        }
    }, 5000);
}

// Функция для удаления уведомления
function removeNotification(notification) {
    notification.style.animation = 'slideOut 0.5s ease-in-out';
    setTimeout(() => {
        if (notification.parentElement) {
            notification.parentElement.removeChild(notification);
        }
    }, 500);
}