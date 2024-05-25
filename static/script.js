// Функция для загрузки информации о задаче или событии в модальное окно
function loadRecordData(recordId, recordType) {
    // Отправляем GET запрос на сервер для получения данных о задаче или событии
    fetch(`/get_record_info/${recordType}/${recordId}`)
        .then(response => response.json())
        .then(data => {
            // Вставляем полученные данные в соответствующие поля формы
            document.getElementById('viewRecordTitle').value = data.title;
            document.getElementById('viewRecordDescription').value = data.description;
            document.getElementById('viewRecordDate').value = data.date;

            var editButton = document.getElementById('editRecordBtn');
            var deleteButton = document.getElementById('deleteRecordBtn');

            console.log(data)

            // Дополнительно, если есть поля приоритета и статуса, обновите их значения, если они возвращаются с сервера
            if (data.type === 'event') {
                console.log(data.id)
                editButton.dataset.recordId = data.id;
                editButton.dataset.recordType = "event";
                deleteButton.dataset.recordId = data.id;
                deleteButton.dataset.recordType = "event";
                document.getElementById('viewRecordPriority').value = data.priority;
                document.getElementById('viewRecordPriorityContainer').style.display = 'block';
                document.getElementById('viewRecordPriorityContainer').remove();
                document.getElementById('viewRecordStatusContainer').remove();
            }
            if (data.type === 'task') {
                console.log(data.id)
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

                document.getElementById('viewRecordPriorityContainer').style.display = 'block';
                document.getElementById('viewRecordStatusContainer').style.display = 'block';
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
    // Подтверждаем действие удаления
    if (confirm('Вы уверены, что хотите удалить эту запись?')) {
        // Отправляем DELETE запрос на сервер для удаления записи
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
    document.getElementById('viewRecordTitle').removeAttribute('readonly');
    document.getElementById('viewRecordDescription').removeAttribute('readonly');
    document.getElementById('viewRecordDate').removeAttribute('readonly');
    document.getElementById('viewRecordPriority').removeAttribute('readonly');
    document.getElementById('viewRecordStatus').removeAttribute('readonly');

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
    document.getElementById('viewRecordTitle').removeAttribute('readonly');
    document.getElementById('viewRecordDescription').removeAttribute('readonly');
    document.getElementById('viewRecordDate').removeAttribute('readonly');
    console.log("editEvent")



}

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

    const cancelButton = document.createElement('button');
    cancelButton.type = 'button';
    cancelButton.className = 'btn btn-secondary';
    cancelButton.setAttribute('data-bs-dismiss', 'modal');
    cancelButton.textContent = 'Отмена';

    const saveButton = document.createElement('button');
    saveButton.type = 'submit';
    saveButton.className = 'btn btn-primary';
    saveButton.setAttribute('id', 'ConfirmEditRecordBtn');
    saveButton.setAttribute('data-record-id', recordId);
    saveButton.setAttribute('data-record-type', recordType);
    saveButton.textContent = 'Сохранить';

    modalFooter.appendChild(cancelButton);
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


