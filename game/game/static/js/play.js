var player = "Meu Player"
var other_players = ["A", "B", "C", "D", "E"]
var currentLetter = "A"
var otherAnswers = {"A": {"MSE": ""}}

function generateAnalysisTable(){
	
}

function cleanAnalyisisTable(){

}

function startNewRound(letter){
	oldLetters.append(currentLetter);
	currentLetter = letter;
	updateHtmlNewLetter(letter);
	cleanAnalysisTable();
	restartTimer();
}

function requestStop(){
	alert("STOP requested");
	return false;
}

function answerStop(){
	sendCurrentAnswers();
}

function sendCurrentAnswers(){

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
	return false;
}

function requestOtherAnswers(){

}

function startAnalyzingAnswers(){

}

function doCheck(){
	if(isRoundOver()){
		answerStop();
		otherAnswers = null;
		while(!otherAnswers){
			otherAnswers = requestOtherAnswers();
		}
		startAnalyzingAnswers();
	}
}

function updateClock(time){
	clock = clock - time;
	$('#clock').text(clock);
}

var checkInterval = setInterval(doCheck, 1000);
setInterval("updateClock(1)",1000);