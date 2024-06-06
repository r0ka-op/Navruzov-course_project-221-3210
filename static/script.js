// Функция для загрузки информации о задаче или событии в модальное окно
function loadRecordData(recordId, recordType) {
    // Отправляем GET запрос на сервер для получения данных о задаче или событии
    fetch(`/get_record_info/${recordType}/${recordId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('viewRecordModal').removeAttribute('data-bs-backdrop');

            document.getElementById('viewRecordTitle').value = data.title;
            document.getElementById('viewRecordDescription').value = data.description;
            document.getElementById('viewRecordDate').value = data.date;

            var editButton = document.getElementById('editRecordBtn');
            var deleteButton = document.getElementById('deleteRecordBtn');

            console.log(data)

            // Дополнительно, если есть поля приоритета и статуса, обновите их значения, если они возвращаются с сервера
            if (data.type === 'event') {
                console.log(data.id)
                document.getElementById('viewRecordModalLabel').innerText = 'Просмотр События';
                editButton.dataset.recordId = data.id;
                editButton.dataset.recordType = "event";
                deleteButton.dataset.recordId = data.id;
                deleteButton.dataset.recordType = "event";
            }
            if (data.type === 'task') {
                console.log(data.id)
                document.getElementById('viewRecordModalLabel').innerText = 'Просмотр Задачи';

                editButton.dataset.recordId = data.id;
                editButton.dataset.recordType = "task";
                deleteButton.dataset.recordId = data.id;
                deleteButton.dataset.recordType = "task";
                console.log(data.status)
                if (data.status)
                    document.getElementById('viewRecordStatus').value = "Не выполнено";
                else
                    document.getElementById('viewRecordStatus').value = "Выполнено";

                if (data.priority === 1)
                    document.getElementById('viewRecordPriority').value = "Низкий";
                else if (data.priority === 2)
                    document.getElementById('viewRecordPriority').value = "Средний";
                else if (data.priority === 3)
                    document.getElementById('viewRecordPriority').value = "Высокий";
            }
        })
        .catch(error => console.error('Ошибка при загрузке данных о задаче или событии:', error));
}

// Обработчик события клика на кнопку открытия модального окна
document.querySelectorAll('.get-info').forEach(btn => {
    btn.addEventListener('click', function() {
        // Получаем ID и тип записи из data-атрибутов кнопки
        const recordId = this.dataset.recordId;
        const recordType = this.dataset.recordType;

        // Загружаем данные о записи в модальное окно
        loadRecordData(recordId, recordType);
    });
});


// Функция для удаления записи (задачи или события)
function deleteRecord(recordId, recordType) {
    if (confirm('Вы уверены, что хотите удалить эту запись?')) {
        fetch(`/delete_record/${recordType}/${recordId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Запись успешно удалена');
                // Перезагружаем страницу для обновления списка записей
                window.location.reload();
            } else {
                alert('Ошибка при удалении записи');
            }
        })
        .catch(error => console.error('Ошибка при удалении записи:', error));
    }
}

document.getElementById('deleteRecordBtn').onclick = function () {
    var recordId = this.getAttribute('data-record-id');
    var recordType = this.getAttribute('data-record-type');
    deleteRecord(recordId, recordType);
};


// Функция для удаления записи (задачи или события)
function updateRecord(recordId, recordType) {
    var title = document.getElementById('viewRecordTitle').value;
    var description = document.getElementById('viewRecordDescription').value;
    var date = document.getElementById('viewRecordDate').value;

    var updatedData = {
        title: title,
        description: description,
        date: date
    };

    if (recordType === 'task') {
        var priority = document.getElementById('recordPriority').value;
        console.log(priority)
        var status = document.getElementById('recordStatus').value;
        console.log(status)
        updatedData.priority = priority;
        updatedData.status = status;
    }

    console.log(updatedData)

    fetch(`/update_record/${recordType}/${recordId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updatedData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Запись успешно обновлена');
            // Закрыть модальное окно и обновить данные на странице
            var modal = bootstrap.Modal.getInstance(document.getElementById('viewRecordModal'));
            modal.hide();
            location.reload(); // Перезагрузка страницы для обновления данных
        } else {
            console.error('Ошибка при обновлении записи:', data.message);
        }
    })
    .catch(error => console.error('Ошибка при отправке запроса на изменение записи:', error));
}

function editTask() {
    document.getElementById('viewRecordModalLabel').innerText = 'Изменение Задачи';
    document.getElementById('viewRecordTitle').removeAttribute('readonly');
    document.getElementById('viewRecordDescription').removeAttribute('readonly');
    document.getElementById('viewRecordDate').removeAttribute('readonly');
    document.getElementById('viewRecordPriority').removeAttribute('readonly');
    document.getElementById('viewRecordStatus').removeAttribute('readonly');

    document.getElementById('viewRecordPriorityContainer').style.display = 'block';
    document.getElementById('viewRecordStatusContainer').style.display = 'block';

    // Меняем тип ячейки Приоритет
    const inputElement = document.getElementById('viewRecordPriority');
    const inputValue = inputElement.value;     // Получаем значение <input>

    const selectElementPriority = document.createElement('select');
    selectElementPriority.className = 'form-select';
    selectElementPriority.id = 'recordPriority';
    selectElementPriority.name = 'recordPriority';
    selectElementPriority.required = true;

    const optionsPriority = [
        { value: '1', text: 'Низкий' },
        { value: '2', text: 'Средний' },
        { value: '3', text: 'Высокий' }
    ];

    optionsPriority.forEach(optionData => {
        const option = document.createElement('option');
        option.value = optionData.value;
        option.text = optionData.text;

        if (optionData.value === inputValue) {
            option.selected = true;
        }

        selectElementPriority.appendChild(option);
    });

    inputElement.parentNode.replaceChild(selectElementPriority, inputElement);


    // Меняем тип ячейки статус
    var statusInput = document.getElementById('viewRecordStatus');

    var selectElementStatus = document.createElement('select');
    selectElementStatus.className = 'form-select';
    selectElementStatus.id = 'recordStatus';
    selectElementStatus.name = 'recordStatus';
    selectElementStatus.required = true;

    var optionsStatus = [
        { value: '1', text: 'Выполнено' },
        { value: '0', text: 'Не выполнено' }
    ];

    optionsStatus.forEach(function(optionData) {
        var option = document.createElement('option');
        option.value = optionData.value;
        option.text = optionData.text;
        selectElementStatus.appendChild(option);
    });

    statusInput.parentNode.replaceChild(selectElementStatus, statusInput);
}

function editEvent() {
    document.getElementById('viewRecordModalLabel').innerText = 'Изменение События';
    document.getElementById('viewRecordTitle').removeAttribute('readonly');
    document.getElementById('viewRecordDescription').removeAttribute('readonly');
    document.getElementById('viewRecordDate').removeAttribute('readonly');
    console.log("editEvent")
}


// Функция для редактирования записи
document.getElementById('editRecordBtn').onclick = function () {
    var recordId = this.getAttribute('data-record-id');
    var recordType = this.getAttribute('data-record-type');

    if (recordType === 'task')
        editTask();
    else
        editEvent();

    // Меняем кнопки
    const modalFooter = document.getElementById('view_edit_footer');

    modalFooter.innerHTML = '';

    document.getElementById('viewRecordModal').setAttribute('data-bs-backdrop', 'static');


    const saveButton = document.createElement('button');
    saveButton.type = 'submit';
    saveButton.className = 'btn btn-primary';
    saveButton.setAttribute('id', 'ConfirmEditRecordBtn');
    saveButton.setAttribute('data-record-id', recordId);
    saveButton.setAttribute('data-record-type', recordType);
    saveButton.textContent = 'Сохранить';

    modalFooter.appendChild(saveButton);



    document.getElementById('ConfirmEditRecordBtn').onclick = function () {

        console.log(123456);
        var recordId = this.getAttribute('data-record-id');
        var recordType = this.getAttribute('data-record-type');
        console.log(recordId);
        console.log(recordType);


        updateRecord(recordId, recordType);
    };
}


// Функция для экспорта данных
document.getElementById('btn-export').addEventListener('click', function() {
    // Отправляем GET-запрос на сервер для экспорта CSV
    fetch('/export_csv', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/csv'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            throw new Error('Ошибка при экспорте данных');
        }
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'data_export.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при экспорте данных');
    });
});


// Функция для импорта данных
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('import-form').addEventListener('submit', function(event) {
        event.preventDefault();

        let formData = new FormData(this);

        fetch('/import_csv', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Ошибка:', data.error);
                alert('Ошибка: ' + data.error);
            } else {
                console.log('Успех:', data.message);
                alert('Успех: ' + data.message);
                location.reload();
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Ошибка: ' + error);
        });
    });
});

function formatDate(dateString) {
    const date = new Date(dateString);

    const daysOfWeek = ["воскресенье", "понедельник", "вторник", "среда", "четверг", "пятница", "суббота"];
    const dayOfWeek = daysOfWeek[date.getUTCDay()];
    const day = String(date.getUTCDate()).padStart(2, '0');
    const month = String(date.getUTCMonth() + 1).padStart(2, '0'); // Месяцы в JavaScript начинаются с 0
    const year = date.getUTCFullYear();

    return `${dayOfWeek} ${day}-${month}-${year}`;
}


// Функция для поиска по названию
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const originalTasks = document.getElementById('task-list').innerHTML;
    const originalEvents = document.getElementById('event-list').innerHTML;

    searchInput.addEventListener('input', function() {
        let query = searchInput.value;
        let startDate = startDateInput.value;
        let endDate = endDateInput.value;

        if (startDate && !endDate) {
            endDate = new Date().toISOString().split('T')[0];
        } else if (!startDate && endDate) {
            startDate = endDate;
        }

        if (query.length >= 1 || startDate || endDate) {
            fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({
                    'query': query,
                    'start_date': startDate,
                    'end_date': endDate
                })
            })
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
                        taskList.appendChild(document.createElement('br'));
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

                // Если списки пусты, отобразить сообщение об отсутствии результатов
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
            .catch(error => console.error('Error:', error));
        } else if (query.length === 0) {
            document.getElementById('task-list').innerHTML = originalTasks;
            document.getElementById('event-list').innerHTML = originalEvents;
        }
    });
});


// Функция для поиска по диапазону дат
document.getElementById('search-btn').addEventListener('click', function() {
    var startDate = document.getElementById('start-date').value;
    var endDate = document.getElementById('end-date').value;

    // Если введена только одна дата, установим вторую на сегодняшнюю
    if (startDate && !endDate) {
        endDate = new Date().toISOString().split('T')[0];
        document.getElementById('end-date').value = endDate;
    } else if (!startDate && endDate) {
        startDate = new Date().toISOString().split('T')[0];
        document.getElementById('start-date').value = startDate;
    }


    var searchParams = new URLSearchParams({
        'start_date': startDate,
        'end_date': endDate
    });

    fetch('/search_by_date?' + searchParams.toString())
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            console.log(data);
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
                    taskList.appendChild(document.createElement('br'));
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
        .catch(function(error) {
            console.error('Error:', error);
        });
});
