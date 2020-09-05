function getQuestions(i) {
    const container = document.createElement('div');
    container.className = 'form-row';

    const childContainer = document.createElement('div');
    childContainer.className = 'col-md-4 mb-3';

    const option_label = document.createElement('label');
    option_label.htmlFor = `option_${i}`;
    option_label.innerHTML = `Вариант ${i + 1}`;

    const option_input = document.createElement('input');
    option_input.className = "form-control"
    option_input.type = 'text';
    option_input.id = `option_${i}`;
    option_input.name = `option_${i}`;
    option_input.required = 'required';

    option_label.appendChild(option_input);


    const radioContainer = document.createElement('div');
    radioContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const is_true_input = document.createElement('input');
    is_true_input.className = "custom-control-input"
    is_true_input.type = 'radio';
    is_true_input.id = `is_true_${i}`;
    is_true_input.name = `is_true`;
    is_true_input.value = `${i}`;

    const is_true_label = document.createElement('label');
    is_true_label.className = 'custom-control-label'
    is_true_label.htmlFor = `is_true_${i}`;
    is_true_label.innerHTML = 'Верный ответ';

    radioContainer.appendChild(is_true_input);
    radioContainer.appendChild(is_true_label);

    childContainer.appendChild(option_label);
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

    const option_label = document.createElement('label');
    option_label.htmlFor = `option_${i}`;
    option_label.innerHTML = `Вариант ${i + 1}`;

    const option_input = document.createElement('input');
    option_input.className = "form-control-file"
    option_input.type = 'file';
    option_input.id = `option_${i}`;
    option_input.name = `option_${i}`;
    option_input.required = 'required';
    option_input.accept="image/*"

    fileContainer.appendChild(option_label);
    fileContainer.appendChild(option_input);

    const radioContainer = document.createElement('div');
    radioContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const is_true_input = document.createElement('input');
    is_true_input.className = "custom-control-input"
    is_true_input.type = 'radio';
    is_true_input.id = `is_true_${i}`;
    is_true_input.name = `is_true`;
    is_true_input.value = `${i}`;

    const is_true_label = document.createElement('label');
    is_true_label.className = 'custom-control-label'
    is_true_label.htmlFor = `is_true_${i}`;
    is_true_label.innerHTML = 'Верный ответ';

    radioContainer.appendChild(is_true_input);
    radioContainer.appendChild(is_true_label);

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

    const option_label = document.createElement('label');
    option_label.htmlFor = `option_${i}`;
    option_label.innerHTML = `Вариант ${i + 1}`;

    const option_input = document.createElement('input');
    option_input.className = "form-control"
    option_input.type = 'text';
    option_input.id = `option_${i}`;
    option_input.name = `option_${i}`;
    option_input.required = 'required';

    option_label.appendChild(option_input);


    const checkboxContainer = document.createElement('div');
    checkboxContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const is_true_input = document.createElement('input');
    is_true_input.className = "custom-control-input"
    is_true_input.type = 'checkbox';
    is_true_input.id = `is_true_${i}`;
    is_true_input.name = `is_true_${i}`;

    const is_true_label = document.createElement('label');
    is_true_label.className = 'custom-control-label'
    is_true_label.htmlFor = `is_true_${i}`;
    is_true_label.innerHTML = 'Верный ответ';

    checkboxContainer.appendChild(is_true_input);
    checkboxContainer.appendChild(is_true_label);

    childContainer.appendChild(option_label);
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

    const option_input = document.createElement('input');
    option_input.className = "form-control-file"
    option_input.type = 'file';
    option_input.id = `option_${i}`;
    option_input.name = `option_${i}`;
    option_input.required = 'required';
    option_input.accept="image/*"

    fileContainer.appendChild(option_label);
    fileContainer.appendChild(option_input);


    const checkboxContainer = document.createElement('div');
    checkboxContainer.className = 'custom-control custom-checkbox my-1 mr-sm-2';

    const is_true_input = document.createElement('input');
    is_true_input.className = "custom-control-input"
    is_true_input.type = 'checkbox';
    is_true_input.id = `is_true_${i}`;
    is_true_input.name = `is_true_${i}`;

    const is_true_label = document.createElement('label');
    is_true_label.className = 'custom-control-label'
    is_true_label.htmlFor = `is_true_${i}`;
    is_true_label.innerHTML = 'Верный ответ';

    checkboxContainer.appendChild(is_true_input);
    checkboxContainer.appendChild(is_true_label);

    childContainer.appendChild(fileContainer);
    childContainer.appendChild(checkboxContainer);

    container.appendChild(childContainer);

    return container;
}

function addQuestionMain() {
    const questions = document.getElementById('add-question-questions-div');

    const tasks_num = document.getElementById('add-question-tasks-num');
    tasks_num.onkeyup = tasks_num.onchange = () => {
        const count = +(tasks_num.value);
        questions.innerHTML = '';
        for (let i = 0; i < count; ++i) {
            if (document.getElementById('multiselect').checked) {
                if (document.getElementById('with_images').checked) {
                    questions.appendChild(getQuestionsWithMultiselectAndImages(i));
                } else {
                    questions.appendChild(getQuestionsWithMultiselect(i));
                }
            } else {
                if (document.getElementById('with_images').checked) {
                    questions.appendChild(getQuestionsWithImages(i))
                } else {
                    questions.appendChild(getQuestions(i));
                }
            }
        }
    };

    const multiselect = document.getElementById('multiselect');
    multiselect.onkeyup = multiselect.onchange = () => {
        const count = +(tasks_num.value);
        questions.innerHTML = '';
        for (let i = 0; i < count; ++i) {
            if (document.getElementById('multiselect').checked) {
                if (document.getElementById('with_images').checked) {
                    questions.appendChild(getQuestionsWithMultiselectAndImages(i));
                } else {
                    questions.appendChild(getQuestionsWithMultiselect(i));
                }
            } else {
                if (document.getElementById('with_images').checked) {
                    questions.appendChild(getQuestionsWithImages(i))
                } else {
                    questions.appendChild(getQuestions(i));
                }
            }
        }
    };

    const with_images = document.getElementById('with_images');
    with_images.onkeyup = with_images.onchange = () => {
        const count = +(tasks_num.value);
        questions.innerHTML = '';
        for (let i = 0; i < count; ++i) {
            if (document.getElementById('multiselect').checked) {
                if (document.getElementById('with_images').checked) {
                    questions.appendChild(getQuestionsWithMultiselectAndImages(i));
                } else {
                    questions.appendChild(getQuestionsWithMultiselect(i));
                }
            } else {
                if (document.getElementById('with_images').checked) {
                    questions.appendChild(getQuestionsWithImages(i))
                } else {
                    questions.appendChild(getQuestions(i));
                }
            }
        }
    };
}
