function requestStop(){
	alert("STOP requested");
}

function appendNewLetter(letter){
	let = letter.toUpperCase();
	console.log($('.field').append('<div class="input-group input-group-sm">'+
                '<span class="input-group-addon">'+let+'</span>'+
                '<input type="text" class="form-control" placeholder="'+let+'"></div>'));
}

function updateHtmlNewLetter(letter){
	$("input").prop('disabled', true);
	appendNewLetter(letter);
}