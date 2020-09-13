function runTest(timeLeft, postUrl, token) {
    if (timeLeft < 0) {
       document.getElementById("stop-button").click();
       return;
    }
    if (timeLeft % 5 === 0) {
    	$.post(postUrl, {
    		csrfmiddlewaretoken: token
		}).done(function(response) {
			timeLeft = response['time_left'];
			if (timeLeft < 0) {
			   document.getElementById("stop-button").click();
			}
		});
    }
    document.getElementById("time").value = timeLeft;
    document.getElementById("time-div").innerHTML = `Времени осталось: ${timeLeft} с`;
    timeLeft--;
    setTimeout(runTest, 1000, timeLeft, postUrl, token);
}
