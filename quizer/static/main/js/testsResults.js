function getTestOption(test) {
    const option = document.createElement('option');
    option.value = test.name;
    option.innerHTML = test.name;
    return option
}

function getTrElement(counter, result) {
    const tr = document.createElement('tr');

    const counterTd = document.createElement('td');
    counterTd.scope = "row";
    const strongCounter = document.createElement('strong');
    strongCounter.innerHTML = counter;
    counterTd.appendChild(strongCounter);

    const dateTd = document.createElement('td');
    dateTd.innerHTML = result.date;

    const studentsCountTd = document.createElement('td');
    studentsCountTd.innerHTML = result.results.length;

    const refTd = document.createElement('td');
    const ref = document.createElement('a');
    ref.type = 'button';
    ref.className = 'btn btn-primary btn-sm';
    ref.href = `/test_results/${result.id}`;
    ref.innerHTML = 'Посмотреть детальный результат &raquo;';
    refTd.appendChild(ref);

    tr.appendChild(counterTd);
    tr.appendChild(dateTd);
    tr.appendChild(studentsCountTd);
    tr.appendChild(refTd);

    return tr;
}

function main(resultsJson, subjectsJson, testsJson, lecturersJson) {
    const results = JSON.parse(resultsJson
        .replace(/&quot;/gi, '"')
        .replace(/True/gi, 'true')
        .replace(/False/gi, 'false')
        .replace(/None/gi, 'null'));
    let subjectsArray = JSON.parse(subjectsJson.replace(/&quot;/gi, '"'));
    let subjectsMap = new Map();
    for (let subject of subjectsArray) {
        subjectsMap[subject.name.toString()] = subject.id;
    }

    let lecturersArray = JSON.parse(lecturersJson.replace(/&quot;/gi, '"'));
    let lecturersMap = new Map();
    for (let lecturer of lecturersArray) {
        lecturersMap[lecturer.name.toString()] = lecturer.id;
    }

    let testsArray = JSON.parse(testsJson.replace(/&quot;/gi, '"'));
    let testsMap = new Map();
    for (let test of testsArray) {
        testsMap[test.name.toString()] = test.id;
    }

    const tableBody = document.getElementById("table_body");

    const subjectSelect = document.getElementById("subject");
    const lecturerSelect = document.getElementById("lecturer");
    const testSelect = document.getElementById("test");

    let counter = 1;
    for (const test of testsArray) {
        if (test.subject_id == subjectsMap[subjectSelect.options[0].text]) {
            testSelect.appendChild(getTestOption(test));
        }
    }
    for (const result of results) {
        if (result.subject_id == subjectsMap[subjectSelect.options[0].text]) {
            if (result.launched_lecturer_id == lecturersMap[lecturerSelect.options[0].text]) {
                if (result.test_id == testsMap[testSelect.options[0].text]) {
                    tableBody.appendChild(getTrElement(counter, result));
                    counter += 1;
                }
            }
        }
    }

    subjectSelect.onkeyup = subjectSelect.onchange = () =>  {
        tableBody.innerHTML = '';
        testSelect.innerHTML = '';
        counter = 1;
        for (const test of testsArray) {
            if (test.subject_id == subjectsMap[subjectSelect.options[subjectSelect.selectedIndex].text]) {
                testSelect.appendChild(getTestOption(test));
            }
        }
        for (const result of results) {
            if (result.subject_id == subjectsMap[subjectSelect.options[subjectSelect.selectedIndex].text]) {
                if (result.launched_lecturer_id == lecturersMap[lecturerSelect.options[lecturerSelect.selectedIndex].text]) {
                    if (result.test_id == testsMap[testSelect.options[testSelect.selectedIndex].text]) {
                        tableBody.appendChild(getTrElement(counter, result));
                        counter += 1;
                    }
                }
            }
        }
    };

    lecturerSelect.onkeyup = lecturerSelect.onchange = () =>  {
        tableBody.innerHTML = '';
        counter = 1;
        for (const result of results) {
            if (result.subject_id == subjectsMap[subjectSelect.options[subjectSelect.selectedIndex].text]) {
                if (result.launched_lecturer_id == lecturersMap[lecturerSelect.options[lecturerSelect.selectedIndex].text]) {
                    if (result.test_id == testsMap[testSelect.options[testSelect.selectedIndex].text]) {
                        tableBody.appendChild(getTrElement(counter, result));
                        counter += 1;
                    }
                }
            }
        }
    };

    testSelect.onkeyup = testSelect.onchange = () =>  {
        tableBody.innerHTML = '';
        counter = 1;
        for (const result of results) {
            if (result.subject_id == subjectsMap[subjectSelect.options[subjectSelect.selectedIndex].text]) {
                if (result.launched_lecturer_id == lecturersMap[lecturerSelect.options[lecturerSelect.selectedIndex].text]) {
                    if (result.test_id == testsMap[testSelect.options[testSelect.selectedIndex].text]) {
                        tableBody.appendChild(getTrElement(counter, result));
                        counter += 1;
                    }
                }
            }
        }
    };
}
