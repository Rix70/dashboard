// Добавляем функцию для отображения графика
let parameterChart = null;
let currentChartData = null;
let chartModal = null;

function showParameterChart(paramName, paramId) {
    const startDate = sessionStorage.getItem('start_date');
    const endDate = sessionStorage.getItem('end_date');
    
    // Инициализируем модальное окно при первом вызове
    const modalElement = document.getElementById('chartModal');
    if (!chartModal) {
        chartModal = new bootstrap.Modal(modalElement, {
            keyboard: true,
            backdrop: true
        });
    }
    
    fetch('/get_parameter_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify({
            parameter_id: paramId,
            start_date: startDate,
            end_date: endDate
        })
    })
    .then(response => response.json())
    .then(data => {
        currentChartData = data;
        createChart(paramName, data);
        
        // Устанавливаем начальные значения осей
        const validValues = data.values.filter(v => v !== null);
        if (validValues.length > 0) {
            const minValue = Math.min(...validValues);
            const maxValue = Math.max(...validValues);
            document.getElementById('minY').value = Math.floor(minValue);
            document.getElementById('maxY').value = Math.ceil(maxValue);
        }
        
        // Показываем модальное окно
        chartModal.show();
    })
    .catch(error => {
        console.error('Error loading chart data:', error);
        alert('Ошибка при загрузке данных графика');
    });
}

function createChart(paramName, data) {
    const ctx = document.getElementById('parameterChart').getContext('2d');
    
    if (parameterChart) {
        parameterChart.destroy();
    }
    
    parameterChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [{
                label: paramName,
                data: data.values,
                borderColor: '#1976D2',
                backgroundColor: 'rgba(33, 150, 243, 0.1)',
                borderWidth: 2,
                tension: 0.1,
                fill: true,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 14
                        }
                    }
                },
                title: {
                    display: true,
                    text: paramName,
                    font: {
                        size: 18,
                        weight: 'bold'
                    },
                    padding: 20
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    titleColor: '#000',
                    bodyColor: '#000',
                    borderColor: '#ddd',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false,
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 14
                    },
                    callbacks: {
                        label: function(context) {
                            let value = context.raw;
                            return value !== null ? value.toFixed(2) : 'Нет данных';
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                },
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

function updateChartAxes() {
    const minY = parseFloat(document.getElementById('minY').value);
    const maxY = parseFloat(document.getElementById('maxY').value);
    
    if (!isNaN(minY) && !isNaN(maxY) && minY < maxY) {
        parameterChart.options.scales.y.min = minY;
        parameterChart.options.scales.y.max = maxY;
        parameterChart.update();
    }
}

function resetChartAxes() {
    if (currentChartData && currentChartData.values) {
        const validValues = currentChartData.values.filter(v => v !== null);
        if (validValues.length > 0) {
            const minValue = Math.min(...validValues);
            const maxValue = Math.max(...validValues);
            
            document.getElementById('minY').value = Math.floor(minValue);
            document.getElementById('maxY').value = Math.ceil(maxValue);
            
            parameterChart.options.scales.y.min = undefined;
            parameterChart.options.scales.y.max = undefined;
            parameterChart.update();
        }
    }
}

// Инициализация обработчиков событий
document.addEventListener('DOMContentLoaded', function() {
    const modalElement = document.getElementById('chartModal');
    
    // Очистка при закрытии
    modalElement.addEventListener('hidden.bs.modal', function() {
        if (parameterChart) {
            parameterChart.destroy();
            parameterChart = null;
        }
    });
    
    // Обновление размера при открытии
    modalElement.addEventListener('shown.bs.modal', function() {
        if (parameterChart) {
            parameterChart.resize();
        }
    });
    
    // Обработка клавиши Esc
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && chartModal) {
            chartModal.hide();
        }
    });
});