function getResultsTable(finishedStudentsResults, idx) {
    const table = document.createElement('table');
    table.setAttribute('id', `table_${idx}`);
    table.setAttribute('class', "table table-hover");

    const thead = document.createElement('thead');
    thead.innerHTML = `
        <tr>
            <th>#</th>
            <th>Слушатель</th>
            <th>Результат</th>
            <th>Время прохождения</th>
            <th>Время завершения</th>
        </tr>`;

    const tbody = document.createElement('tbody');
    for (let i = 0; i < finishedStudentsResults.length; i++) {
        const tr = document.createElement('tr');
        let result = finishedStudentsResults[i];
        tr.innerHTML = `
            <td scope="row"><strong>${i + 1}</strong></td>
            <td>${result.user.username}</td>
            <td>${result.right_answers_count}/${result.tasks_num}</td>
            <td>${result.time} c</td>
            <td>${result.date}</td>`;
        tbody.appendChild(tr);
    }

    table.appendChild(thead);
    table.appendChild(tbody);
    return table;
}

function getRunningTestDiv(testResult, idx) {
    const container = document.createElement('div');

    const hr = document.createElement('hr');
    hr.setAttribute('class', "my-4");

    const label = document.createElement('label');
    label.setAttribute('htmlfor', 'test_name');

    const nameH3 = document.createElement('h3');
    nameH3.innerText = testResult.test.name;

    const descP = document.createElement('p');
    descP.innerText = testResult.test.description;

    const infoP = document.createElement('p');
    infoP.innerHTML = `<img src='${refsDict.researchIcon}'> Количество заданий в тесте: ${testResult.test.tasks_num}<br>
        <img src='${refsDict.clockIcon}'> Время на выполнение: ${testResult.test.duration} c<br>
        <span class="pointer" onclick='hideTable("search_${idx}", "table_${idx}")' title="Нажмите, чтобы скрыть результаты">
              <img src='${refsDict.teamIcon}'> Выполнило слушателей: ${testResult.results.length}
        </span>`;

    const searchInput = document.createElement('input');
    searchInput.setAttribute('class', "form-control");
    searchInput.setAttribute('type', "text");
    searchInput.setAttribute('placeholder', "Искать...");
    searchInput.setAttribute('id', `search_${idx}`);
    searchInput.setAttribute('onkeyup', `tableSearch("search_${idx}", "table_${idx}")`);

    const resultsTable = getResultsTable(testResult.results, idx);
    const form = document.createElement('form');
    form.setAttribute('action', refsDict.formUrl);
    form.setAttribute('method', 'post');
    form.innerHTML = refsDict.csrfToken + `<input type="hidden" name="test_id", value="${testResult.test.id}"> 
        <button class="btn btn-danger"><img src='${refsDict.stopIcon}'> Оcтановить</button>`;

    label.appendChild(hr);
    label.appendChild(nameH3);
    label.appendChild(descP);
    label.appendChild(infoP);
    label.appendChild(searchInput);
    label.appendChild(resultsTable);
    label.appendChild(form);
    
    container.appendChild(label)
    return container;
}

function renderRunningTests() {
    let runningTestsResults = [];
    $.get(runningTestsAPIUrl)
        .done(function (response) {
            runningTestsResults = response['tests'];
            runningTestsDiv.innerHTML = '';
            for (let i = 0; i < runningTestsResults.length; i++) {
                runningTestsDiv.appendChild(getRunningTestDiv(runningTestsResults[i], i));
            }
        });
}