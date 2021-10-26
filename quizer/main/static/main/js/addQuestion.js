function getQuestionOption(i) {
    const container = document.createElement('div');
    container.className = 'form-row';

    const childContainer = document.createElement('div');
    childContainer.className = 'col-md-4 mb-3';

    const optionLabel = document.createElement('label');
    optionLabel.htmlFor = `option_${i}`;
    optionLabel.innerHTML = `Вариант ${i + 1}`;

    const optionTextarea = document.createElement('textarea');
    optionTextarea.className = "form-control option-input";
    optionTextarea.type = 'text';
    optionTextarea.id = `option_${i}`;
    optionTextarea.name = `option_${i}`;

    optionLabel.appendChild(optionTextarea);


    const radioContainer = document.createElement('div');
    radioContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const isTrueInput = document.createElement('input');
    isTrueInput.className = "custom-control-input is-true-input";
    isTrueInput.type = 'radio';
    isTrueInput.id = `is_true_${i}`;
    isTrueInput.name = `is_true`;
    isTrueInput.value = `${i}`;

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

function getQuestionOptionWithImages(i) {
    const container = document.createElement('div');
    container.className = 'form-row';

    const childContainer = document.createElement('div');
    childContainer.className = 'col-md-4 mb-3';


    const fileContainer = document.createElement('div');
    fileContainer.className = 'form-group';

    const optionLabel = document.createElement('label');
    optionLabel.htmlFor = `option_${i}`;
    optionLabel.innerHTML = `Вариант ${i + 1}`;

    const optionInput = document.createElement('input');
    optionInput.className = "form-control-file option-input";
    optionInput.type = 'file';
    optionInput.id = `option_${i}`;
    optionInput.name = `option_${i}`;
    optionInput.required = 'required';
    optionInput.accept = "image/*";

    fileContainer.appendChild(optionLabel);
    fileContainer.appendChild(optionInput);

    const radioContainer = document.createElement('div');
    radioContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const isTrueInput = document.createElement('input');
    isTrueInput.className = "custom-control-input is-true-input";
    isTrueInput.type = 'radio';
    isTrueInput.id = `is_true_${i}`;
    isTrueInput.name = `is_true`;
    isTrueInput.value = `${i}`;

    const isTrueLabel = document.createElement('label');
    isTrueLabel.className = 'custom-control-label';
    isTrueLabel.htmlFor = `is_true_${i}`;
    isTrueLabel.innerHTML = 'Верный ответ';

    radioContainer.appendChild(isTrueInput);
    radioContainer.appendChild(isTrueLabel);

    childContainer.appendChild(fileContainer);
    childContainer.appendChild(radioContainer);

    container.appendChild(childContainer);

    return container;
}

function getQuestionOptionWithMultiselect(i) {
    const container = document.createElement('div');
    container.className = 'form-row';

    const childContainer = document.createElement('div');
    childContainer.className = 'col-md-4 mb-3';

    const optionLabel = document.createElement('label');
    optionLabel.htmlFor = `option_${i}`;
    optionLabel.innerHTML = `Вариант ${i + 1}`;

    const optionTextarea = document.createElement('input');
    optionTextarea.className = "form-control option-input";
    optionTextarea.type = 'text';
    optionTextarea.id = `option_${i}`;
    optionTextarea.name = `option_${i}`;

    optionLabel.appendChild(optionTextarea);


    const checkboxContainer = document.createElement('div');
    checkboxContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const isTrueInput = document.createElement('input');
    isTrueInput.className = "custom-control-input is-true-input";
    isTrueInput.type = 'checkbox';
    isTrueInput.id = `is_true_${i}`;
    isTrueInput.name = `is_true_${i}`;

    const isTrueLabel = document.createElement('label');
    isTrueLabel.className = 'custom-control-label';
    isTrueLabel.htmlFor = `is_true_${i}`;
    isTrueLabel.innerHTML = 'Верный ответ';

    checkboxContainer.appendChild(isTrueInput);
    checkboxContainer.appendChild(isTrueLabel);

    childContainer.appendChild(optionLabel);
    childContainer.appendChild(checkboxContainer);

    container.appendChild(childContainer);

    return container;
}

function getQuestionOptionWithMultiselectAndImages(i) {
    const container = document.createElement('div');
    container.className = 'form-row';

    const childContainer = document.createElement('div');
    childContainer.className = 'col-md-4 mb-3';


    const fileContainer = document.createElement('div');
    fileContainer.className = 'form-group';

    const option_label = document.createElement('label');
    option_label.htmlFor = `option_${i}`;
    option_label.innerHTML = `Вариант ${i + 1}`;

    const optionInput = document.createElement('input');
    optionInput.className = "form-control-file option-input";
    optionInput.type = 'file';
    optionInput.id = `option_${i}`;
    optionInput.name = `option_${i}`;
    optionInput.required = 'required';
    optionInput.accept = "image/*";

    fileContainer.appendChild(option_label);
    fileContainer.appendChild(optionInput);


    const checkboxContainer = document.createElement('div');
    checkboxContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const isTrueInput = document.createElement('input');
    isTrueInput.className = "custom-control-input is-true-input";
    isTrueInput.type = 'checkbox';
    isTrueInput.id = `is_true_${i}`;
    isTrueInput.name = `is_true_${i}`;

    const isTrueLabel = document.createElement('label');
    isTrueLabel.className = 'custom-control-label';
    isTrueLabel.htmlFor = `is_true_${i}`;
    isTrueLabel.innerHTML = 'Верный ответ';

    checkboxContainer.appendChild(isTrueInput);
    checkboxContainer.appendChild(isTrueLabel);

    childContainer.appendChild(fileContainer);
    childContainer.appendChild(checkboxContainer);

    container.appendChild(childContainer);

    return container;
}

function renderAddQuestionModal() {
    const questions = document.getElementById('add-question-questions-div');

    const tasksNum = document.getElementById('add-question-tasks-num');
    const multiselect = document.getElementById('add-question-multiselect');
    const withImages = document.getElementById('add-question-with-images');

    tasksNum.onkeyup = tasksNum.onchange
        = multiselect.onkeyup = multiselect.onchange
        = withImages.onkeyup = withImages.onchange = () => {
        const count = +(tasksNum.value);
        questions.innerHTML = '';
        for (let i = 0; i < count; ++i) {
            if (multiselect.checked) {
                if (withImages.checked) {
                    questions.appendChild(getQuestionOptionWithMultiselectAndImages(i));
                } else {
                    questions.appendChild(getQuestionOptionWithMultiselect(i));
                }
            } else {
                if (withImages.checked) {
                    questions.appendChild(getQuestionOptionWithImages(i))
                } else {
                    questions.appendChild(getQuestionOption(i));
                }
            }
        }
    };
}

function cleanUpAddQuestionModal() {
    const getById = (id) => {
        return document.getElementById(id);
    };

    const optionsDiv = getById("add-question-questions-div");
    const qstnFormulation = getById("add-question-formulation");
    const tasksNum = getById("add-question-tasks-num");
    const withImages = getById("add-question-with-images");
    const multiselect = getById("add-question-multiselect");

    optionsDiv.innerHTML = '';
    qstnFormulation.value = '';
    tasksNum.value = '';
    withImages.checked = false;
    multiselect.checked = false


}

function addQuestion() {
    const getById = (id) => {
        return document.getElementById(id);
    };
    const qstnFormulation = getById("add-question-formulation").value;
    const testID = getById("add-question-test-id").value;
    const tasksNum = getById("add-question-tasks-num").value;
    const withImages = getById("add-question-with-images").checked;
    const multiselect = getById("add-question-multiselect").checked;
    const optionTextareas = document.getElementsByClassName('option-input');
    const isTrueInputs = document.getElementsByClassName('is-true-input');

    let formData = new FormData();
    formData.append('test_id', testID);
    formData.append('multiselect', multiselect);
    formData.append('with_images', withImages);
    formData.append('formulation', qstnFormulation);
    formData.append('tasks_num', tasksNum);

    if (!withImages) {
        let options = [];
        for (let i = 0; i < optionTextareas.length; i++) {
            options.push({
                option: optionTextareas[i].value,
                is_true: isTrueInputs[i].checked
            });
        }
        formData.append('options', JSON.stringify(options));
    } else {
        for (let i = 0; i < optionTextareas.length; i++) {
            let file = optionTextareas[i].files[0];
            formData.append(file.name, isTrueInputs[i].checked);
            formData.append(file.name, file);
        }
    }

    $.ajax({
        url: questionsAPIUrl.replace('test_id', testID.toString()),
        type: 'post',
        data: formData,
        contentType: false,
        processData: false,
        headers: {'X-CSRFToken': csrfToken},
        success: (response) => {
            if (response['success'] !== undefined) {
                cleanUpAddQuestionModal();
                renderTests();
                renderInfoModalWindow("Вопрос добавлен", response['success']);
            } else {
                renderInfoModalWindow("Ошибка", response['error']);
            }
        }
    });
}