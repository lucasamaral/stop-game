var player = "Meu Player"
var clock = 100
var maxClock = 100
var fields = ["MSE", "PCH", "Carro"]
var otherPlayers = ["P1", "P2", "P3", "P4", "P5"]
var currentLetter = ""
var oldLetters = []
var otherAnswers = {"A": {"MSE": ""}}
var CurrentAnswers = {}
var clockInterval = null;
var checkInterval = null;

var tempStop = false;

function generateAnalysisTable(){
	console.log("Generating analysis table")
	console.log(otherAnswers)
	strrr = "<table class=\"table\"><tr><th></th>"
	for(pl in otherPlayers){
		player = otherPlayers[pl]
		console.log(player);
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
        		"<input type=\"checkbox\">"+
      			"</span>"+
      			"<input type=\"text\" id=\""+player+"-"+field+"\" class=\"form-control\" disabled placeholder=\""+otherAnswers[player][field]+"\">"+
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
}

function sendAnalysis(){
	console.log("Sending Analysis")
}

function appendNewLetter(letter){
	let = letter.toUpperCase();
	$('.field').append('<div class="input-group input-group-sm">'+
                '<span class="input-group-addon">'+let+'</span>'+
                '<input type="text" class="form-control" placeholder="'+let+'"></div>');
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
	return {"P1": {"MSE": "AA", "MSE": "BB", "PCH": "CC","Carro": "VV"},
			"P2": {"MSE": "DD", "MSE": "PP", "PCH": "EE","Carro": "UU"},
			"P3": {"MSE": "GG", "MSE": "OO", "PCH": "FF","Carro": "TT"},
			"P4": {"MSE": "KK", "MSE": "NN", "PCH": "HH","Carro": "SS"},
			"P5": {"MSE": "LL", "MSE": "MM", "PCH": "QQ","Carro": "RR"},}
}

function updateClock(time){
	clock = clock - time;
	$('#clock').text(clock);
	if(clock > 0){
		setTimeout("updateClock(1)",1000);
	}
}

function startNewRound(letter){
	oldLetters.push(currentLetter);
	currentLetter = letter;
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