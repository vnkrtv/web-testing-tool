function getTimeLeft(post_url, csrf_token) {
	let xhr = new XMLHttpRequest();

	xhr.open('POST', post_url);
	xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xhr.onload = function() {
	    if (xhr.status === 200) {
	        if (xhr.responseText < 0) {
	        	document.getElementById("stop-button").click();
	        }
	    }
	    else if (xhr.status !== 200) {
	        console.log("Error on sending post request.");
	    }
	};
	xhr.send(encodeURI(`csrfmiddlewaretoken=${csrf_token}`));
}


function runTest(timeLeft, post_url, csrf_token) {
    if (timeLeft < 0) {
       document.getElementById("stop-button").click();
       return;
    }
    if (timeLeft % 5 == 0) {
    	getTimeLeft(post_url, csrf_token);
    }
    document.getElementById("time").value = timeLeft;
    document.getElementById("time-div").innerHTML = `Времени осталось: ${timeLeft} с`;
    timeLeft--;
    setTimeout(runTest, 1000, timeLeft, post_url, csrf_token);
}
