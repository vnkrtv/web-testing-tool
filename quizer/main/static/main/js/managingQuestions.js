function getQuestionOption(i, value, isTrue) {
    const container = document.createElement('div');
    container.className = 'form-row';

    const childContainer = document.createElement('div');
    childContainer.className = 'col-md-4 mb-3';

    const optionLabel = document.createElement('label');
    optionLabel.htmlFor = `option_${i}`;
    optionLabel.innerHTML = `Вариант ${i + 1}`;

    const optionInput = document.createElement('input');
    optionInput.className = "form-control"
    optionInput.type = 'text';
    optionInput.id = `option_${i}`;
    optionInput.name = `option_${i}`;
    optionInput.required = 'required';
    optionInput.value = value;

    optionLabel.appendChild(optionInput);


    const radioContainer = document.createElement('div');
    radioContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const isTrueInput = document.createElement('input');
    isTrueInput.className = "custom-control-input"
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
    optionInput.className = "form-control"
    optionInput.type = 'text';
    optionInput.id = `option_${i}`;
    optionInput.name = `option_${i}`;
    optionInput.required = 'required';
    optionInput.value = value;

    optionLabel.appendChild(optionInput);


    const checkboxContainer = document.createElement('div');
    checkboxContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const isTrueInput = document.createElement('input');
    isTrueInput.className = "custom-control-input"
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

    const option_label = document.createElement('label');
    option_label.htmlFor = `option_${i}`;
    option_label.innerHTML = `Вариант ${i + 1}`;

    const optionRef = document.createElement('a');
    optionRef.className = "form-control-file";
    optionRef.href = mediaUrl + value;
    optionRef.innerHTML = 'Посмотреть';

    fileContainer.appendChild(option_label);
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
    const hiddenMultelelectInput = document.getElementById('hidden-question-multiselect');
    multiselectInput.checked = (question.multiselect === true) ? 'checked' : '';
    hiddenMultelelectInput.value = (question.multiselect === true) ? 'on' : '';

    const withImageInput = document.getElementById('question-with-images');
    const hiddenWithImagesInput = document.getElementById('hidden-question-with-images');
    withImageInput.checked = (question.type === 'image') ? 'checked' : '';
    hiddenWithImagesInput.value = (question.type === 'image') ? 'on' : '';

    const optionsDiv = document.getElementById('options-div');
    optionsDiv.innerHTML = '';
    for (let t = 0; t < question.options.length; t++) {
        if (question.type == '') {
            if (question.multiselect) {
                optionsDiv.appendChild(getQuestionOptionWithMultiselect(
                        t, question.options[t].option, question.options[t].is_true))
            } else {
                optionsDiv.appendChild(getQuestionOption(
                        t, question.options[t].option, question.options[t].is_true))
            }
        } else if (question.type == 'image') {
            if (question.multiselect) {
                optionsDiv.appendChild(getQuestionOptionWithMultiselectAndImages(
                        t, question.options[t].option, question.options[t].is_true))
            } else {
                optionsDiv.appendChild(getQuestionOptionWithImages(
                        t, question.options[t].option, questions[i].options[t].is_true))
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

    const overlay = document.getElementById('overlay');
    overlay.classList.toggle('active');
}