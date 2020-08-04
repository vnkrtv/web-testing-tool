function getDivElement(i, tests) {
    const container = document.createElement('div');

    const hr = document.createElement('hr');
    hr.className = "my-4";

    const label = document.createElement('label');
    label.htmlFor = "test_name";

    const test_name_h3 = document.createElement('h3');
    test_name_h3.innerHTML = `${tests[i].name}`;

    const description_p = document.createElement('p');
    description_p.innerHTML = `${tests[i].description}`;

    const info_p = document.createElement('p');
    info_p.innerHTML = `Предмет: ${tests[i].subject.name }<br>
    Количество заданий в тесте: ${tests[i].tasks_num}<br>
    Время на выполнение: ${tests[i].duration} с`;

    const btn = document.createElement('button');
    btn.className = "btn btn-primary";
    btn.innerHTML = "Запустить";
    btn.id =  "test_name";
    btn.name =  "test_id";
    btn.value = `${tests[i].id}`;

    label.appendChild(test_name_h3);
    label.appendChild(description_p);
    label.appendChild(info_p);
    label.appendChild(btn);

    container.appendChild(hr);
    container.appendChild(label);

    return container;
}

function main(testsJson) {
    const tests = JSON.parse(testsJson.replace(/&quot;/gi, '"'));
    const tests_count = parseInt(tests.length);
    const tests_container = document.getElementById("tests_container");

    const subject = document.getElementById("subject");
    const name_filter = document.getElementById("name_filter");

    for (let i = 0; i < tests_count; ++i) {
        if (tests[i].subject.name == subject.options[0].text) {
            tests_container.appendChild(getDivElement(i, tests));
        }
    }

    subject.onkeyup = subject.onchange = () =>  {
        tests_container.innerHTML = '';
        for (let i = 0; i < tests_count; ++i) {
            if (tests[i].name.includes(name_filter.value)) {
                if (tests[i].subject.name == subject.options[subject.selectedIndex].text) {
                    tests_container.appendChild(getDivElement(i, tests));
                }
            }
        }
    };

    name_filter.onkeyup = name_filter.onchange = () =>  {
        tests_container.innerHTML = '';
        for (let i = 0; i < tests_count; ++i) {
            if (tests[i].name.includes(name_filter.value)) {
                if (tests[i].subject.name == subject.options[subject.selectedIndex].text) {
                    tests_container.appendChild(getDivElement(i, tests));
                }
            }
        }
    };
}
