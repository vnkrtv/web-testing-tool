function tableSearch(input_id, table_id) {
    const phrase = document.getElementById(input_id);
    const table = document.getElementById(table_id);
    const regPhrase = new RegExp(phrase.value, 'i');
    let flag = false;
    for (let i = 1; i < table.rows.length; i++) {
        flag = false;
        for (let j = table.rows[i].cells.length - 1; j >= 0; j--) {
            flag = regPhrase.test(table.rows[i].cells[j].innerHTML);
            if (flag) break;
        }
        if (flag) {
            table.rows[i].style.display = "";
        } else {
            table.rows[i].style.display = "none";
        }
    }
}

function sortTableByNums(table_id, column_num, has_child) {
    const table = document.getElementById(table_id);
    let rows, i, x, y, shouldSwitch;
    let switchCount = 0;
    let switching = true;
    let dir = "asc";

    while (switching) {
        switching = false;
        rows = table.rows;

        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;

            x = rows[i].getElementsByTagName("TD")[column_num];
            if (has_child) {
                x = x.firstChild;
            }
            y = rows[i + 1].getElementsByTagName("TD")[column_num];
            if (has_child) {
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

function sortTable(table_id, column_num) {
    const table = document.getElementById(table_id);
    let rows, i, x, y, shouldSwitch;
    let switchCount = 0;
    let switching = true;
    let dir = "asc";

    while (switching) {
        switching = false;
        rows = table.rows;

        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;

            x = rows[i].getElementsByTagName("TD")[column_num];
            y = rows[i + 1].getElementsByTagName("TD")[column_num];
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

function hideTable(input_id, table_id) {
    if (document.getElementById(input_id).style.display === "") {
        document.getElementById(input_id).style.display = "none";
    } else {
        document.getElementById(input_id).style.display = "";
    }
    if (document.getElementById(table_id).style.display === "") {
        document.getElementById(table_id).style.display = "none";
    } else {
        document.getElementById(table_id).style.display = "";
    }
}

function fillErrorsModal(rowID, testResults) {
    const container = document.getElementById('errors-container');
    container.innerHTML = "";
    const resultID = parseInt(rowID.split("_")[1]);
    const questions = testResults.results[resultID]['questions'];

    for (let i in questions) {
        const li = document.createElement("li");
        if (questions[i]["is_true"]) {
            li.className = "list-group-item list-group-item-success";
            li.innerHTML = `${i}. Верно`;
        } else {
            li.className = "list-group-item list-group-item-danger";
            li.innerHTML = `${i}. Ошибка<br>
            Выбрано: ${questions[i]["selected_answers"]}<br>
            Верно: ${questions[i]["right_answers"]}`;
        }
        container.appendChild(li);
    }
}
