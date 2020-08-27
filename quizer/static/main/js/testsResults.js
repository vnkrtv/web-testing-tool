function getTrElement(i, results) {
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
    info_p.innerHTML = `<img src='${staticPath}main/images/subject.svg'> Предмет: ${tests[i].subject.name }<br>
    <img src='${staticPath}main/images/research.svg'> Количество заданий в тесте: ${tests[i].tasks_num}<br>
    <img src='${staticPath}main/images/clock.svg'> Время на выполнение: ${tests[i].duration} с`;

    const btn = document.createElement('button');
    btn.className = "btn btn-primary";
    btn.innerHTML = `<img src='${staticPath}main/images/play.svg'> Запустить`;
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

function main(resultsJson) {
    const results = JSON.parse(resultsJson.replace(/&quot;/gi, '"'));
    const resultsCount = parseInt(results.length);
    const tableBody = document.getElementById("table_body");

    const subject = document.getElementById("subject");
    const lecturer = document.getElementById("lecturer");
    const test = document.getElementById("test");

    for (let i = 0; i < resultsCount; ++i) {
        if (results[i].subject_id === subject.options[0].text) {
            tests_container.appendChild(getDivElement(i, tests, staticPath));
        }
    }

    subject.onkeyup = subject.onchange = () =>  {
        tableBody.innerHTML = '';
        for (let i = 0; i < resultsCount; ++i) {
            if (tests[i].name.includes(name_filter.value)) {
                if (tests[i].subject.name == subject.options[subject.selectedIndex].text) {
                    tests_container.appendChild(getDivElement(i, tests, staticPath));
                }
            }
        }
    };

    lecturer.onkeyup = lecturer.onchange = () =>  {
        tableBody.innerHTML = '';
        for (let i = 0; i < resultsCount; ++i) {
            if (tests[i].name.includes(name_filter.value)) {
                if (tests[i].subject.name == subject.options[subject.selectedIndex].text) {
                    tests_container.appendChild(getDivElement(i, tests, staticPath));
                }
            }
        }
    };

    test.onkeyup = test.onchange = () =>  {
        tableBody.innerHTML = '';
        for (let i = 0; i < tests_count; ++i) {
            if (tests[i].name.includes(name_filter.value)) {
                if (tests[i].subject.name == subject.options[subject.selectedIndex].text) {
                    tests_container.appendChild(getDivElement(i, tests, staticPath));
                }
            }
        }
    };
}
