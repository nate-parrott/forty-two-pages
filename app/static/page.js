function __edit() {
	$('#__content').load('/__meta/source'+location.pathname, null, function(_,_,_) {
		$(document.body).css({"overflow-x": "hidden"}); // work around super-annoying scrollbar bug
		$('#__content').attr('contentEditable', true).focus();
		document.execCommand("enableObjectResizing", true, true);
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
