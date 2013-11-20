var tempStop = false;

$.ajaxSetup({ 
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
         }
         return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     } 
});

function generateAnalysisTable(){
	console.log("Generating analysis table")
	strrr = "<table class=\"table\"><tr><th></th>"
	for(pl in otherPlayers){
		player = otherPlayers[pl]
		strrr = strrr.concat("<th>"+player+"</th>");
	}
	strrr = strrr.concat("</tr>");
	for(f in fields){
		field = fields[f]
		strrr = strrr.concat("<tr><td>"+field+"</td>")
		for(pl in otherPlayers){
			player = otherPlayers[pl]
			strrr = strrr.concat("<td>"+ "<div class=\"input-group\">"+
      			"<span class=\"input-group-addon\">"+
        		"<input id=\""+player+"-"+field+"\" type=\"checkbox\">"+
      			"</span>"+
      			"<input type=\"text\" class=\"form-control\" disabled placeholder=\""+otherAnswers[player][field]+"\">"+
    			"</div>"+"</td>");
		}
		strrr = strrr.concat("</tr>");
	}
	strrr = strrr.concat("</table><button onclick=\"return sendAnalysis()\" class=\"btn\">Enviar</button>");
	$('#analysis-table').append(strrr);
}

function restartTimer(){
	clock = maxClock;
	setTimeout("updateClock(1)",1000);
}

function cleanAnalysisTable(){
	$('#analysis-table').empty();
}

function requestStop(){
	tempStop = true;
	return false;
}

function answerStop(){
	console.log("Respondendo stop");
	sendCurrentAnswers();
}

function sendCurrentAnswers(){
	console.log("Mandando respostas");
	var data = {}
	for(fi in fields){
		field = fields[fi]
		data[field] = $('#'+field+'-'+currentRound).val();
	}
	$.post('/send-answers/', JSON.stringify(data));
}

function waitForNextRound(){
	if(false){
		setTimeout("waitForNextRound()", 2000);
	}else{
		tempStop = false;
		startNewRound("B")
	}
}

function sendAnalysis(){
	console.log("Sending Analysis")
	data = {}
	for(pl in otherPlayers){
		player = otherPlayers[pl];
		data[player] = {}
		for(fi in fields){
			field = fields[fi]
			data[player][field] = $('#'+player+"-"+field).is(':checked')
		}
	}
	console.log(data)
	cleanAnalysisTable();
	waitForNextRound();
}

function appendNewLetter(letter){
	let = letter.toUpperCase();
	for(fi in fields){
		field = fields[fi]
		$('#field-'+field).append('<div class="input-group input-group-sm">'+
                '<span class="input-group-addon">'+let+'</span>'+
                '<input type="text" id="'+field+"-"+currentRound+'" class="form-control" placeholder="'+let+'"></div>');
	}
}

function updateHtmlNewLetter(letter){
	$("input").prop('disabled', true);
	appendNewLetter(letter);
}

function isRoundOver(){
	return tempStop;
}

function requestOtherAnswers(){
	console.log("Requesting other answers")
	var data = {}
	$.ajax({url: '/everyone-answers/',
			success: function(a){
						data = a
					},
			async: false});
	return data
}

function updateClock(time){
	clock = clock - time;
	$('#clock').text(clock);
	if(clock > 0 && !tempStop){
		setTimeout("updateClock(1)",1000);
	}
}

function startNewRound(letter){
	oldLetters.push(currentLetter);
	currentLetter = letter;
	currentRound +=1;
	$("#current-round").text(currentRound);
	updateHtmlNewLetter(letter);
	cleanAnalysisTable();
	restartTimer();
	setTimeout("doCheck()", 5000);
}

function finishRound(){
	answerStop();
	otherAnswers = null;
	while(!otherAnswers){
		otherAnswers = requestOtherAnswers();
	}
	generateAnalysisTable();
}

function doCheck(){
	console.log("Checking");
	if(isRoundOver()){
		console.log("Round is over");
		finishRound();
	}else{
		setTimeout("doCheck()", 5000);
	}
}