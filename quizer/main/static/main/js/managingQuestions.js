function getQuestionOption(i, value, isTrue) {
    const container = document.createElement('div');
    container.className = 'form-row';

    const childContainer = document.createElement('div');
    childContainer.className = 'col-md-4 mb-3';

    const optionLabel = document.createElement('label');
    optionLabel.htmlFor = `option_${i}`;
    optionLabel.innerHTML = `Вариант ${i + 1}`;

    const optionInput = document.createElement('input');
    optionInput.className = "form-control option-input"
    optionInput.type = 'text';
    optionInput.id = `option_${i}`;
    optionInput.name = `option_${i}`;
    optionInput.required = 'required';
    optionInput.value = value;

    optionLabel.appendChild(optionInput);


    const radioContainer = document.createElement('div');
    radioContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const isTrueInput = document.createElement('input');
    isTrueInput.className = "custom-control-input is-true-input"
    isTrueInput.type = 'radio';
    isTrueInput.id = `is_true_${i}`;
    isTrueInput.name = `is_true`;
    isTrueInput.value = `${i}`;
    isTrueInput.checked = (isTrue === true) ? 'checked' : '';

    const isTrueLabel = document.createElement('label');
    isTrueLabel.className = 'custom-control-label'
    isTrueLabel.htmlFor = `is_true_${i}`;
    isTrueLabel.innerHTML = 'Верный ответ';

    radioContainer.appendChild(isTrueInput);
    radioContainer.appendChild(isTrueLabel);

    childContainer.appendChild(optionLabel);
    childContainer.appendChild(radioContainer);

    container.appendChild(childContainer);

    return container;
}

function getQuestionOptionWithImages(i, value, isTrue) {
    const container = document.createElement('div');
    container.className = 'form-row';

    const childContainer = document.createElement('div');
    childContainer.className = 'col-md-4 mb-3';


    const fileContainer = document.createElement('div');
    fileContainer.className = 'form-group';

    const optionLabel = document.createElement('label');
    optionLabel.htmlFor = `option_${i}`;
    optionLabel.innerHTML = `Вариант ${i + 1}`;

    const optionRef = document.createElement('a');
    optionRef.className = "form-control-file";
    optionRef.href = mediaUrl + value;
    optionRef.innerHTML = 'Посмотреть';

    fileContainer.appendChild(optionLabel);
    fileContainer.appendChild(optionRef);

    const radioContainer = document.createElement('div');
    radioContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const isTrueInput = document.createElement('input');
    isTrueInput.className = "custom-control-input"
    isTrueInput.type = 'radio';
    isTrueInput.id = `is_true_${i}`;
    isTrueInput.name = `is_true`;
    isTrueInput.value = `${i}`;
    isTrueInput.checked = (isTrue === true) ? 'checked' : '';
    isTrueInput.disabled = 'disabled';

    const isTrueLabel = document.createElement('label');
    isTrueLabel.className = 'custom-control-label'
    isTrueLabel.htmlFor = `is_true_${i}`;
    isTrueLabel.innerHTML = 'Верный ответ';

    radioContainer.appendChild(isTrueInput);
    radioContainer.appendChild(isTrueLabel);

    childContainer.appendChild(fileContainer);
    childContainer.appendChild(radioContainer);

    container.appendChild(childContainer);

    return container;
}

function getQuestionOptionWithMultiselect(i, value, isTrue) {
    const container = document.createElement('div');
    container.className = 'form-row';

    const childContainer = document.createElement('div');
    childContainer.className = 'col-md-4 mb-3';

    const optionLabel = document.createElement('label');
    optionLabel.htmlFor = `option_${i}`;
    optionLabel.innerHTML = `Вариант ${i + 1}`;

    const optionInput = document.createElement('input');
    optionInput.className = "form-control option-input"
    optionInput.type = 'text';
    optionInput.id = `option_${i}`;
    optionInput.name = `option_${i}`;
    optionInput.required = 'required';
    optionInput.value = value;

    optionLabel.appendChild(optionInput);


    const checkboxContainer = document.createElement('div');
    checkboxContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const isTrueInput = document.createElement('input');
    isTrueInput.className = "custom-control-input is-true-input"
    isTrueInput.type = 'checkbox';
    isTrueInput.id = `is_true_${i}`;
    isTrueInput.name = `is_true_${i}`;
    isTrueInput.checked = (isTrue === true) ? 'checked' : '';

    const isTrueLabel = document.createElement('label');
    isTrueLabel.className = 'custom-control-label'
    isTrueLabel.htmlFor = `is_true_${i}`;
    isTrueLabel.innerHTML = 'Верный ответ';

    checkboxContainer.appendChild(isTrueInput);
    checkboxContainer.appendChild(isTrueLabel);

    childContainer.appendChild(optionLabel);
    childContainer.appendChild(checkboxContainer);

    container.appendChild(childContainer);

    return container;
}

function getQuestionOptionWithMultiselectAndImages(i, value, isTrue) {
    const container = document.createElement('div');
    container.className = 'form-row';

    const childContainer = document.createElement('div');
    childContainer.className = 'col-md-4 mb-3';


    const fileContainer = document.createElement('div');
    fileContainer.className = 'form-group';

    const optionLabel = document.createElement('label');
    optionLabel.htmlFor = `option_${i}`;
    optionLabel.innerHTML = `Вариант ${i + 1}`;

    const optionRef = document.createElement('a');
    optionRef.className = "form-control-file";
    optionRef.href = mediaUrl + value;
    optionRef.innerHTML = 'Посмотреть';

    fileContainer.appendChild(optionLabel);
    fileContainer.appendChild(optionRef);


    const checkboxContainer = document.createElement('div');
    checkboxContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const isTrueInput = document.createElement('input');
    isTrueInput.className = "custom-control-input"
    isTrueInput.type = 'checkbox';
    isTrueInput.id = `is_true_${i}`;
    isTrueInput.name = `is_true_${i}`;
    isTrueInput.checked = (isTrue === true) ? 'checked' : '';
    isTrueInput.disabled = 'disabled';

    const isTrueLabel = document.createElement('label');
    isTrueLabel.className = 'custom-control-label'
    isTrueLabel.htmlFor = `is_true_${i}`;
    isTrueLabel.innerHTML = 'Верный ответ';

    checkboxContainer.appendChild(isTrueInput);
    checkboxContainer.appendChild(isTrueLabel);

    childContainer.appendChild(fileContainer);
    childContainer.appendChild(checkboxContainer);

    container.appendChild(childContainer);

    return container;
}

function fillQuestionModal(i) {
    const question = questions[i];

    const formulationInput = document.getElementById('question-formulation');
    formulationInput.value = question.formulation;

    const optionsNumInput = document.getElementById('question-tasks-num');
    optionsNumInput.value = question.tasks_num;

    const multiselectInput = document.getElementById('question-multiselect');
    const hiddenMultiselectInput = document.getElementById('hidden-question-multiselect');
    multiselectInput.checked = (question.multiselect === true) ? 'checked' : '';
    hiddenMultiselectInput.value = (question.multiselect === true) ? 'on' : '';

    const withImageInput = document.getElementById('question-with-images');
    const hiddenWithImagesInput = document.getElementById('hidden-question-with-images');
    withImageInput.checked = (question.type === 'image') ? 'checked' : '';
    hiddenWithImagesInput.value = (question.type === 'image') ? 'on' : '';

    const optionsDiv = document.getElementById('options-div');
    optionsDiv.innerHTML = '';
    for (let idx = 0; idx < question.options.length; idx++) {
        if (question.type === '') {
            if (question.multiselect) {
                optionsDiv.appendChild(getQuestionOptionWithMultiselect(
                    idx, question.options[idx].option, question.options[idx].is_true))
            } else {
                optionsDiv.appendChild(getQuestionOption(
                    idx, question.options[idx].option, question.options[idx].is_true))
            }
        } else if (question.type === 'image') {
            if (question.multiselect) {
                optionsDiv.appendChild(getQuestionOptionWithMultiselectAndImages(
                    idx, question.options[idx].option, question.options[idx].is_true))
            } else {
                optionsDiv.appendChild(getQuestionOptionWithImages(
                    idx, question.options[idx].option, questions[i].options[idx].is_true))
            }
        }
    }
    const qstnIDInput = document.getElementById('edit-question-id');
    qstnIDInput.value = question.id;

    const delQstnBtn = document.getElementById('delete-question-button');
    delQstnBtn.setAttribute('onclick', `fillDeleteQuestionModal('${question.id}', ${question.test_id})`);
}

function fillDeleteQuestionModal(qstnID, testID) {
    const qstnFormulationInput = document.getElementById('question-formulation');
    const deleteP = document.getElementById('delete-p');
    deleteP.innerHTML = `Вы действительно хотите удалить вопрос '${qstnFormulationInput.value}'?`;

    const testIDInput = document.getElementById('delete-question-test-id');
    testIDInput.value = testID;

    const qstnIDInput = document.getElementById('delete-question-id');
    qstnIDInput.value = qstnID;

    const editModal = document.getElementById('question-edit-modal');
    editModal.classList.toggle('active');

    const deleteModal = document.getElementById('question-delete-modal');
    deleteModal.classList.toggle('active');
}

function renderQuestionsTable(questionsAPIUrl, questionsTbody) {
    $.get(questionsAPIUrl
    ).done(function (response) {
        questions = response['questions'];
        questionsTbody.innerHTML = '';
        const typesDict = {
            '': 'Обычный',
            'image': 'Изображения'
        }
        for (let i = 0; i < questions.length; i++) {
            let question = questions[i];
            const tr = document.createElement('tr');
            tr.setAttribute('id', `row_${i}`);
            tr.setAttribute('class', 'js-open-modal pointer');
            tr.setAttribute('onclick', `fillQuestionModal(${i})`);
            tr.setAttribute('data-modal', "question-modal");
            tr.innerHTML = `
                <td scope="row"><strong>${i + 1}</strong></td>
                <td>${question.formulation}</td>
                <td>${question.tasks_num}</td>
                <td>${question.multiselect ? '+' : '-'}</td>
                <td>${typesDict[question.type]}</td>`;
            questionsTbody.appendChild(tr);
        }
        activateModalWindows();
    });
}

function editQuestion(questionsAPIUrl, questionsTbody, csrfToken) {
    const getValueById = (id) => {
        return document.getElementById(id).value;
    };
    const qstnID = getValueById("edit-question-id");
    const qstnFormulation = getValueById("question-formulation");
    const withImages = ('on' === getValueById("hidden-question-with-images"));
    const multiselect = ('on' === getValueById("hidden-question-multiselect"));
    const optionInputs = document.getElementsByClassName('option-input');
    const isTrueInputs = document.getElementsByClassName('is-true-input');

    let options = [];
    for (let i = 0; i < optionInputs.length; i++) {
        options.push({
            option: optionInputs[i].value,
            is_true: isTrueInputs[i].checked
        });
    }

    const params = {
        withImages: withImages,
        multiselect: multiselect,
        formulation: qstnFormulation,
        options: JSON.stringify(options),
        csrfmiddlewaretoken: csrfToken
    };
    console.log(params);
    $.post(`${questionsAPIUrl}/${qstnID}`, params)
        .done((response) => {
            renderQuestionsTable(questionsAPIUrl, questionsTbody);
            renderInfoModalWindow("Вопрос отредактирован", response['success']);
        });
}

function deleteQuestion(questionsAPIUrl, questionsTbody, csrfToken) {
    const qstnID = document.getElementById("delete-question-id").value;
    const params = {
        csrfmiddlewaretoken: csrfToken
    };
    $.post(`${questionsAPIUrl}/${qstnID}`, params)
        .done((response) => {
            renderQuestionsTable(questionsAPIUrl, questionsTbody);
            renderInfoModalWindow("Вопрос удален", response['success']);
        });
}
