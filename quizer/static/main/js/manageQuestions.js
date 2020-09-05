function getQuestions(i) {
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

    optionLabel.appendChild(optionInput);


    const radioContainer = document.createElement('div');
    radioContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const isTrueInput = document.createElement('input');
    isTrueInput.className = "custom-control-input"
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

function getQuestionsWithImages(i) {
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
    optionInput.className = "form-control-file"
    optionInput.type = 'file';
    optionInput.id = `option_${i}`;
    optionInput.name = `option_${i}`;
    optionInput.required = 'required';
    optionInput.accept="image/*"

    fileContainer.appendChild(optionLabel);
    fileContainer.appendChild(optionInput);

    const radioContainer = document.createElement('div');
    radioContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const isTrueInput = document.createElement('input');
    isTrueInput.className = "custom-control-input"
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

    childContainer.appendChild(fileContainer);
    childContainer.appendChild(radioContainer);

    container.appendChild(childContainer);

    return container;
}

function getQuestionsWithMultiselect(i) {
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

    optionLabel.appendChild(optionInput);


    const checkboxContainer = document.createElement('div');
    checkboxContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const isTrueInput = document.createElement('input');
    isTrueInput.className = "custom-control-input"
    isTrueInput.type = 'checkbox';
    isTrueInput.id = `is_true_${i}`;
    isTrueInput.name = `is_true_${i}`;

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

function getQuestionsWithMultiselectAndImages(i) {
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
    optionInput.className = "form-control-file"
    optionInput.type = 'file';
    optionInput.id = `option_${i}`;
    optionInput.name = `option_${i}`;
    optionInput.required = 'required';
    optionInput.accept="image/*"

    fileContainer.appendChild(option_label);
    fileContainer.appendChild(optionInput);


    const checkboxContainer = document.createElement('div');
    checkboxContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const isTrueInput = document.createElement('input');
    isTrueInput.className = "custom-control-input"
    isTrueInput.type = 'checkbox';
    isTrueInput.id = `is_true_${i}`;
    isTrueInput.name = `is_true_${i}`;

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

function manageQuestions() {
    const questions = document.getElementById('add-question-questions-div');

    const tasksNum = document.getElementById('add-question-tasks-num');
    const multiselect = document.getElementById('add-question-multiselect');
    const withImages = document.getElementById('add-question-with-images');

    tasksNum.onkeyup = tasksNum.onchange = () => {
        const count = +(tasksNum.value);
        questions.innerHTML = '';
        for (let i = 0; i < count; ++i) {
            if (multiselect.checked) {
                if (withImages.checked) {
                    questions.appendChild(getQuestionsWithMultiselectAndImages(i));
                } else {
                    questions.appendChild(getQuestionsWithMultiselect(i));
                }
            } else {
                if (withImages.checked) {
                    questions.appendChild(getQuestionsWithImages(i))
                } else {
                    questions.appendChild(getQuestions(i));
                }
            }
        }
    };

    multiselect.onkeyup = multiselect.onchange = () => {
        const count = +(tasksNum.value);
        questions.innerHTML = '';
        for (let i = 0; i < count; ++i) {
            if (multiselect.checked) {
                if (withImages.checked) {
                    questions.appendChild(getQuestionsWithMultiselectAndImages(i));
                } else {
                    questions.appendChild(getQuestionsWithMultiselect(i));
                }
            } else {
                if (withImages.checked) {
                    questions.appendChild(getQuestionsWithImages(i))
                } else {
                    questions.appendChild(getQuestions(i));
                }
            }
        }
    };

    withImages.onkeyup = withImages.onchange = () => {
        const count = +(tasksNum.value);
        questions.innerHTML = '';
        for (let i = 0; i < count; ++i) {
            if (multiselect.checked) {
                if (withImages.checked) {
                    questions.appendChild(getQuestionsWithMultiselectAndImages(i));
                } else {
                    questions.appendChild(getQuestionsWithMultiselect(i));
                }
            } else {
                if (withImages.checked) {
                    questions.appendChild(getQuestionsWithImages(i))
                } else {
                    questions.appendChild(getQuestions(i));
                }
            }
        }
    };
}
