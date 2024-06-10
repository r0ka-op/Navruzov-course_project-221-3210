"use strict";

const datetxtEl = document.querySelector(".datetxt");
const datesEl = document.querySelector(".dates");
const btnEl = document.querySelectorAll(".calendar_headings .fa-solid");
const monthYearEl = document.querySelector(".months_year"); // Исправлено: заменено на правильный класс
let dmObj = {
    days: [
        "Вс",
        "Пн",
        "Вт",
        "Ср",
        "Чт",
        "Пт",
        "Сб",
    ],
    months: [
        "Январь",
        "Февраль",
        "Март",
        "Апрель",
        "Май",
        "Июнь",
        "Июль",
        "Август",
        "Сентябрь",
        "Октябрь",
        "Ноябрь",
        "Декабрь",
    ],
};
// объект даты
let dateObj = new Date();
let dayName = dmObj.days[dateObj.getDay()]; // день
let month = dateObj.getMonth(); // месяц
let year = dateObj.getFullYear(); // год
let date = dateObj.getDate(); // дата
// сегодняшняя дата
datetxtEl.innerHTML = `${dayName}, ${date}, ${dmObj.months[month]}, ${year}`;

const displayCalendar = () => {
    let firtDayOfMonth = new Date(year, month, 1).getDay(); // первый день месяца
    let lastDateofMonth = new Date(year, month + 1, 0).getDate(); // последняя дата месяца
    let lastDayofMonth = new Date(year, month, lastDateofMonth).getDay(); // последний день месяца
    let lastDateofLastMonth = new Date(year, month, 0).getDate(); // последняя дата предыдущего месяца
    let days = "";

    // последние дни предыдущего месяца
    for (let i = firtDayOfMonth; i > 0; i--) {
        days += `<li class="dummy">${lastDateofLastMonth - i + 1}</li>`;
    }
    for (let i = 1; i <= lastDateofMonth; i++) {
        let checkToday =
            i === dateObj.getDate() &&
            month === new Date().getMonth() &&
            year === new Date().getFullYear() ?
            "active" :
            "";
        days += `<li class="${checkToday}" data-date="${year}-${month + 1}-${i}">${i}</li>`;
    }
    // первые дни следующего месяца
    for (let i = lastDayofMonth; i < 6; i++) {
        days += `<li class="dummy">${i - lastDayofMonth + 1}</li>`;
    }
    // отображение всех дней внутри HTML
    datesEl.innerHTML = days;

    // Добавляем обработчик событий для клика по дню
    document.querySelectorAll('.dates li:not(.dummy)').forEach(day => {
        day.addEventListener('click', function() {
            const selectedDate = this.dataset.date;
            document.querySelectorAll('.dates li').forEach(d => d.classList.remove('active'));
            this.classList.add('active');
            searchByDate(selectedDate);
        });
    });

    // отображение текущего месяца и года
    monthYearEl.innerHTML = `${dmObj.months[month]}, ${year}`;
};

displayCalendar();

// предыдущий и следующий месяц
btnEl.forEach((btns) => {
    btns.addEventListener("click", () => {
        month = btns.id === "prev" ? month - 1 : month + 1;
        if (month < 0 || month > 11) {
            date = new Date(year, month, new Date().getDate());
            year = date.getFullYear();
            month = date.getMonth();
        } else {
            date = new Date();
        }
        displayCalendar();
    });
});

function searchByDate(date) {
    var searchParams = new URLSearchParams({
        'start_date': date,
        'end_date': date
    });
    console.log(date)
    console.log(searchParams)
    fetch(`/search_by_date?${searchParams.toString()}`)
        .then(response => response.json())
        .then(data => {
            const taskList = document.getElementById('task-list');
            const eventList = document.getElementById('event-list');

            taskList.innerHTML = '';
            eventList.innerHTML = '';

            if (data.tasks.length > 0) {
                data.tasks.forEach(task => {
                    const taskItem = document.createElement('div');
                    taskItem.className = 'card text-center';
                    taskItem.innerHTML = `
              <div class="card-header">
                  ${task.status ? 'Не завершено' : 'Выполнено'}
              </div>
              <div class="card-body">
                  <h5 class="card-title">${task.title}</h5>
                  <p class="card-text">${task.description}</p>
                  <button type="button" class="get-info btn btn-info" data-bs-toggle="modal" data-bs-target="#viewRecordModal" data-record-id="${task.task_id}" data-record-type="task">Подробнее</button>
              </div>
              <div class="card-footer text-body-secondary">
                  Выполнить до: ${formatDate(task.due_date)}
              </div>
          `;
                    taskList.appendChild(taskItem);
                });
            }

            if (data.events.length > 0) {
                data.events.forEach(event => {
                    const eventItem = document.createElement('div');
                    eventItem.className = 'event-item';
                    eventItem.innerHTML = `
              <button type="button" class="btn link-primary get-info" data-bs-toggle="modal" data-bs-target="#viewRecordModal" data-record-id="${event.event_id}" data-record-type="event">${event.title}</button>
          `;
                    eventList.appendChild(eventItem);
                });
            }

            if (taskList.children.length === 0) {
                const noResultsMessage = document.createElement('div');
                noResultsMessage.innerHTML = 'По вашему запросу ничего не найдено.';
                taskList.appendChild(noResultsMessage);
            }
            if (eventList.children.length === 0) {
                const noResultsMessage = document.createElement('div');
                noResultsMessage.innerHTML = 'По вашему запросу ничего не найдено.';
                eventList.appendChild(noResultsMessage);
            }

        })
        .catch(error => console.error('Ошибка при поиске записей на выбранную дату:', error));
}

function formatDate(dateString) {
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', options);
}


document.getElementById('resetBtn').addEventListener('click', function() {
    location.reload();
});

