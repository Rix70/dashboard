class DateSelector {
    constructor() {
        this.MOSCOW_OFFSET = 3;
        this.inputs = {
            start: document.querySelector('input[name="start_date"]'),
            end: document.querySelector('input[name="end_date"]')
        };
        
        if (!this.inputs.start || !this.inputs.end) return;
        
        // Добавляем обработчики событий
        Object.values(this.inputs).forEach(input => {
            input.addEventListener('change', () => this.handleDateChange());
        });

        if (!this.inputs.start.value || !this.inputs.end.value) {
            this.setDefaultDates();
        }
    }
    
    handleDateChange() {
        // Сохраняем в sessionStorage
        Object.entries(this.inputs).forEach(([key, input]) => {
            sessionStorage.setItem(`${key}_date`, input.value);
        });

        // Отправляем данные на сервер
        const formData = new FormData();
        formData.append('start_date', this.inputs.start.value);
        formData.append('end_date', this.inputs.end.value);

        fetch('/update_dates', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        }).then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            }
        }).catch(error => console.error('Error:', error));
    }
    
    setDefaultDates() {
        const now = new Date();
        const dates = {
            start: this.createDate(now, this.MOSCOW_OFFSET, 0),
            end: this.createDate(now, 23 + this.MOSCOW_OFFSET, 59)
        };
        
        Object.entries(dates).forEach(([key, date]) => {
            const dateString = date.toISOString().slice(0, 16);
            this.inputs[key].value = dateString;
            sessionStorage.setItem(`${key}_date`, dateString);
        });

        // Отправляем начальные даты на сервер
        this.handleDateChange();
    }
    
    createDate(baseDate, hours, minutes) {
        const date = new Date(baseDate);
        date.setHours(hours, minutes, 0, 0);
        return date;
    }
}

document.addEventListener('DOMContentLoaded', () => new DateSelector()); 