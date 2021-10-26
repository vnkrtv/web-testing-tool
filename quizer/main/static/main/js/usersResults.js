function getUserTableRow(counter, user) {
    const tr = document.createElement('tr');

    const counterTd = document.createElement('td');
    counterTd.scope = "row";
    const strongCounter = document.createElement('strong');
    strongCounter.innerHTML = counter;
    counterTd.appendChild(strongCounter);

    const usernameTd = document.createElement('td');
    usernameTd.innerHTML = user.username;

    const courceTd = document.createElement('td');
    courceTd.innerHTML = user.course;

    const groupTd = document.createElement('td');
    groupTd.innerHTML = user.group;

    const numberTd = document.createElement('td');
    numberTd.innerHTML = user.number;

    const refTd = document.createElement('td');
    const ref = document.createElement('a');
    ref.type = 'button';
    ref.className = 'btn btn-primary btn-sm';
    ref.href = userResultsUrl.replace('1', user.id);
    ref.innerHTML = 'Перейти к результатам &raquo;';
    refTd.appendChild(ref);

    tr.appendChild(counterTd);
    tr.appendChild(usernameTd);
    tr.appendChild(courceTd);
    tr.appendChild(groupTd);
    tr.appendChild(numberTd);
    tr.appendChild(refTd);

    return tr;
}

function renderUsers() {
    tableBody.innerHTML = '';
    for (let i = 0; i < users.length; i++) {
        tableBody.appendChild(getUserTableRow(i + 1, users[i]));
    }

    const checkGroup = (user) => {
        let selectedGroup = groupSelect.options[groupSelect.selectedIndex].value;
        if (selectedGroup === 'Все')
            return true;
        return user.group.toString() === selectedGroup;
    };

    const checkCourse = (user) => {
        let selectedCourse = courseSelect.options[courseSelect.selectedIndex].value;
        if (selectedCourse === 'Все')
            return true;
        return user.course.toString() === selectedCourse;
    };

    courseSelect.onchange = groupSelect.onchange = () => {
        tableBody.innerHTML = '';
        for (let i = 0; i < users.length; i++) {
            if (checkGroup(users[i]) && checkCourse(users[i])) {
                tableBody.appendChild(getUserTableRow(i + 1, users[i]));
            }
        }
    }
}