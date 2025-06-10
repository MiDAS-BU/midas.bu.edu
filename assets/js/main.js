const publicationsDisplayed = 12;

/* ---- our ideology hover ---- */
$('.process-box').hover(function () {
	$(this).find('.process-intro').hide();
	$(this).find('.process-content').fadeIn();
}, function () {
	$(this).find('.process-content').hide();
	$(this).find('.process-intro').fadeIn();
});

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

/* ---- navbar offset ---- */
function scrollToID(id, speed) {
	var offSet = 69;
	var targetOffset = $(id).offset().top - offSet;
	$('html,body').animate({
		scrollTop: targetOffset
	}, speed);
}

/* ---- close mobile nav on click ---- */
$(document).on('click', '.navbar-collapse.in', function (e) {
	if ($(e.target).is('a') && $(e.target).attr('class') != 'dropdown-toggle') {
		$(this).collapse('hide');
	}
});
