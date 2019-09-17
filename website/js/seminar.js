/* ---- nav smooth scroll ---- */
$(document).ready(function () {
	$('.scroll-link').on('click', function (event) {
		event.preventDefault();
		var sectionID = $(this).attr("data-id");
		scrollToID('#' + sectionID, 750);
	});
	$('.scroll-top').on('click', function (event) {
		event.preventDefault();
		$('html, body').animate({
			scrollTop: 0
		}, 1200);
	});
});