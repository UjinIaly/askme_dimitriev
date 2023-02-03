$('.js-correct-answer').click(function(ev) {
    ev.preventDefault();
    var $this = $(this),
		question_id = $this.data('qid'),
		answer_id = $this.data('aid');

    $.ajax('/correct-answer/', {
    	method: 'POST',
    	data: {
    		question_id: question_id,
    		answer_id: answer_id,
    	},
    }).done(function(response) {
    	console.log("SERVER: " + response);

    	checkbox_id="answer-iscorrect-checkbox-aid-" + answer_id;
		checkbox = $("#" + checkbox_id);
		checkbox.prop('checked', !checkbox.prop('checked'));
    });

    console.log('CLIENT: correct checkbox click   ' + question_id + '   ' + answer_id);
});