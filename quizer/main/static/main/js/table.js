function tableSearch(searchInputID, tableID) {
    const phrase = document.getElementById(searchInputID);
    const table = document.getElementById(tableID);
    const regPhrase = new RegExp(phrase.value.toLowerCase(), 'i');
    let flag = false;
    for (let i = 1; i < table.rows.length; i++) {
        flag = false;
        for (let j = table.rows[i].cells.length - 1; j >= 0; j--) {
            flag = regPhrase.test(table.rows[i].cells[j].innerHTML.toLowerCase());
            if (flag) break;
        }
        if (flag) {
            table.rows[i].style.display = "";
        } else {
            table.rows[i].style.display = "none";
        }
    }
}

function sortTableByNums(tableID, columnNum, hasChild) {
    const table = document.getElementById(tableID);
    let shouldSwitch;
    let i = 0;
    let switchCount = 0;
    let switching = true;
    let dir = "asc";

    while (switching) {
        switching = false;
        let rows = table.rows;

        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;

            let x = rows[i].getElementsByTagName("TD")[columnNum];
            if (hasChild) {
                x = x.firstChild;
            }
            let y = rows[i + 1].getElementsByTagName("TD")[columnNum];
            if (hasChild) {
                y = y.firstChild;
            }
            if (dir === "asc") {
                if (Number(x.innerHTML) > Number(y.innerHTML)) {
                    shouldSwitch = true;
                    break;
                }
            } else if (dir === "desc") {
                if (Number(x.innerHTML) < Number(y.innerHTML)) {
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            switchCount ++;
        } else {
            if (switchCount === 0 && dir === "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}

function sortTable(tableID, columnNum) {
    const table = document.getElementById(tableID);
    let shouldSwitch;
    let i = 0;
    let switchCount = 0;
    let switching = true;
    let dir = "asc";

    while (switching) {
        switching = false;
        let rows = table.rows;

        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;

            let x = rows[i].getElementsByTagName("TD")[columnNum];
            let y = rows[i + 1].getElementsByTagName("TD")[columnNum];
            if (dir === "asc") {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                  shouldSwitch = true;
                  break;
                }
            } else if (dir === "desc") {
            if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                shouldSwitch = true;
                break;
                }
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            switchCount ++;
        } else {
            if (switchCount === 0 && dir === "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}

function hideTable(searchInputID, tableID) {
    const searchInput = document.getElementById(searchInputID);
    const table = document.getElementById(tableID);
    searchInput.style.display = (searchInput.style.display === "") ? "none" : "";
    table.style.display = (table.style.display === "") ? "none" : "";
}

function fillErrorsModal(rowID, testResults, questionsMap, mediaUrl) {
    const container = document.getElementById('errors-container');
    container.innerHTML = "";
    const resultID = parseInt(rowID.split("_")[1]);
    const questions = testResults.results[resultID]['questions'];

    for (let i in questions) {
        const questionLi = document.createElement("li");
        let question = questionsMap.get(questions[i].id);
        questionLi.className = "list-group-item borderless question";
        questionLi.innerText = `${1 + parseInt(i)}. ${question.formulation}`;
        questionLi.style = 'border: 2px solid #FFF; border-radius: 5px;';

        const ul = document.createElement("ul");
        ul.className = "list-group list-group-flush ul-hover";
        questionLi.appendChild(ul);
        console.log(questions[i]);
        for (let option of question.options) {
            const optionLi = document.createElement("li");
            optionLi.className = "list-group-item list-group-item-action";
            optionLi.style = 'border: 2px solid #FFF; border-radius: 5px;';
            if (question.type === '') {
                optionLi.innerText = option.option;
            } else if (question.type === 'image') {
                const imgOption = document.createElement('img');
                imgOption.setAttribute('alt', 'Server pribolel');
                imgOption.setAttribute('height', '341');
                imgOption.setAttribute('style', "width: auto;");
                imgOption.setAttribute('src', mediaUrl + option.option);
                optionLi.appendChild(imgOption);
            }
            if (option.is_true) {
                if (questions[i].selected_answers.indexOf(option.option) !== -1) {
                    optionLi.classList.add('list-group-item-success');
                    optionLi.title = 'Выбран правильный ответ';
                } else {
                    optionLi.classList.add('list-group-item-secondary');
                    optionLi.title = 'Правильный ответ не выбран';
                }
            } else {
                if (questions[i].selected_answers.indexOf(option.option) !== -1) {
                    optionLi.classList.add('list-group-item-danger');
                    optionLi.title = 'Выбран неправильный ответ';
                }
            }
            ul.appendChild(optionLi);
        }
        if (questions[i].is_true) {
            questionLi.classList.add('list-group-item-success');
        } else {
            questionLi.classList.add('list-group-item-danger');
        }
        container.appendChild(questionLi);
    }
}
