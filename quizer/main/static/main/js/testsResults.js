function getTestOption(test) {
    const option = document.createElement('option');
    option.value = test.id;
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
    ref.href = testsResultUrl + result['_id'];
    ref.innerHTML = 'Посмотреть детальный результат &raquo;';
    refTd.appendChild(ref);

    tr.appendChild(counterTd);
    tr.appendChild(dateTd);
    tr.appendChild(studentsCountTd);
    tr.appendChild(refTd);

    return tr;
}

function renderTestResults() {
    const tableBody = document.getElementById("table_body");
    const subjectSelect = document.getElementById("subject");
    const lecturerSelect = document.getElementById("lecturer");
    const testSelect = document.getElementById("test");

    let results = [];
    let tests = [];
    let counter = 1;

    $.get(testsResultsAPIUrl)
        .done(function(response) {
            results = response['results'];
            $.get(testsAPIUrl)
                .done(function(response) {
                    tests = response['tests'];
                    for (const test of tests) {
                        if (test.subject.id.toString() === subjectSelect.options[subjectSelect.selectedIndex].value) {
                            testSelect.appendChild(getTestOption(test));
                        }
                    }
                    for (const result of results) {
                        if (result.subject_id.toString() === subjectSelect.options[subjectSelect.selectedIndex].value) {
                            if (result.launched_lecturer_id.toString() === lecturerSelect.options[lecturerSelect.selectedIndex].value) {
                                if (result.test_id.toString() === testSelect.options[testSelect.selectedIndex].value) {
                                    tableBody.appendChild(getTrElement(counter, result));
                                    counter += 1;
                                }
                            }
                        }
                    }
                });
        });

    subjectSelect.onkeyup = subjectSelect.onchange = () =>  {
        tableBody.innerHTML = '';
        testSelect.innerHTML = '';
        counter = 1;
        for (const test of tests) {
            if (test.subject.id.toString() === subjectSelect.options[subjectSelect.selectedIndex].value) {
                testSelect.appendChild(getTestOption(test));
            }
        }
        for (const result of results) {
            if (result.subject_id.toString() === subjectSelect.options[subjectSelect.selectedIndex].value) {
                if (result.launched_lecturer_id.toString() === lecturerSelect.options[lecturerSelect.selectedIndex].value) {
                    if (result.test_id.toString() === testSelect.options[testSelect.selectedIndex].value) {
                        tableBody.appendChild(getTrElement(counter, result));
                        counter += 1;
                    }
                }
            }
        }
    };

    lecturerSelect.onkeyup = lecturerSelect.onchange
        = testSelect.onkeyup = testSelect.onchange = () =>  {
        tableBody.innerHTML = '';
        counter = 1;
        for (const result of results) {
            if (result.subject_id.toString() === subjectSelect.options[subjectSelect.selectedIndex].value) {
                if (result.launched_lecturer_id.toString() === lecturerSelect.options[lecturerSelect.selectedIndex].value) {
                    if (result.test_id.toString() === testSelect.options[testSelect.selectedIndex].value) {
                        tableBody.appendChild(getTrElement(counter, result));
                        counter += 1;
                    }
                }
            }
        }
    };
}
