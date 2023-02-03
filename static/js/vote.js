$('.js-vote').click(function(ev) {
	ev.preventDefault();
	var $this = $(this),
		action = $this.data('action'),
		object_type = $this.data('type'),
		object_id = $this.data('oid');

	$.ajax('/vote/', {
		method: 'POST',
		data: {
			action: action,
			object_type: object_type,
			object_id: object_id,
		},
	}).done(function(data) {
		new_rating = data['object_rating'];
		console.log("SERVER RESPONSE: new rating is " + new_rating);

		rating_element_id = object_type + "-rating-qid-" + object_id;
		$('#' + rating_element_id).text(new_rating);

		upvote_element_id = object_type + "-upvote-btn-qid-" + object_id;
		downvote_element_id = object_type + "-downvote-btn-qid-" + object_id;
		if (data['action'] == 'like') {
			$('#' + upvote_element_id).addClass('js-vote-inactive');
			$('#' + downvote_element_id).removeClass('js-vote-inactive');
		} else if (data['action'] == 'dislike') {
			$('#' + upvote_element_id).removeClass('js-vote-inactive');
			$('#' + downvote_element_id).addClass('js-vote-inactive');
		} else {
			console.log('uncaught case');
		}
		
	});
	console.log("CLIENT:" + action +  " - " + object_type + " - " + object_id);
});
