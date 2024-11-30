function exportToExcel() {
    const startDate = sessionStorage.getItem('start_date');
    const endDate = sessionStorage.getItem('end_date');
    
    if (!startDate || !endDate) {
        alert('Ошибка: не удалось получить даты. Пожалуйста, обновите страницу.');
        return;
    }

    const pageId = window.location.pathname.split('/').pop();
    if (!pageId || isNaN(pageId)) {
        alert('Ошибка: некорректный ID страницы');
        return;
    }

    const pageName = document.querySelector('h2').textContent.trim();

    const exportButton = document.querySelector('.btn-success');
    const originalText = exportButton.textContent;
    exportButton.textContent = 'Экспорт...';
    exportButton.disabled = true;

    fetch('/export_excel', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content

        },
        body: JSON.stringify({
            start_date: startDate,
            end_date: endDate,
            page_id: pageId
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ошибка при экспорте');
        }
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${pageName}_${startDate.slice(0,10)}_${endDate.slice(0,10)}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    })
    .catch(error => {
        console.error('Ошибка при экспорте:', error);
        alert('Произошла ошибка при экспорте. Пожалуйста, попробуйте еще раз.');
    })
    .finally(() => {
        exportButton.textContent = originalText;
        exportButton.disabled = false;
    });
}