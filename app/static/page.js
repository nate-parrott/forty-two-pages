function __edit() {
	$('#__content').load('/__meta/source'+location.pathname, null, function(_,_,_) {
		$('#__content').attr('contentEditable', true);
	});
	$('#__toolbar').load('/toolbar');
}
$(document).ready(function() {
	$('#__content').click(function(e) {
		var url = $(e.target).attr("download-url");
		if (url) {
			window.open(url);
		}
	})
});
