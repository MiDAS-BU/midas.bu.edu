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

$(document).ready(function () {
	const months = [
		"January",
		"February",
		"March",
		"April",
		"May",
		"June",
		"July",
		"August",
		"September",
		"October",
		"November",
		"December"
	];

	$.getJSON("json/publications.json", publications => {

		var publicationsTemplate = _.template(" \
			<div class=\"col-xs-12 col-sm-12 col-md-6 col-lg-6\"> \
				<h3><%= title %></h3> \
				<p> \
					<%= authors %> \
					<br> \
					<%= venue %>, <%= date.monthTxt %> <%= date.year %> \
					<%= typeof(links) !== 'undefined' && typeof(links.pdf) !== 'undefined' ? '| <a target=\"_blank\" href=\"' + links.pdf + '\">Download PDF</a>' : '' %> \
					<%= typeof(links) !== 'undefined' && typeof(links.abstract) !== 'undefined' ? '| <a target=\"_blank\" href=\"' + links.abstract + '\">External link</a>' : '' %> \
				</p> \
			</div> \
		");

		var publicationHtmlContent = publications
			.sort((a, b) => b.date.year - a.date.year)
			.slice(0, publicationsDisplayed)
			.map(publication => {
				publication.date.monthTxt = publication.date.month != 'undefined' ? months[publication.date.month] : "";

				return publicationsTemplate(publication);
			});

		publicationsHtmlContent = "";
		const inSmall = 1;
		const inMed = 2;
		const inLarge = 2;
		for (let index = 1; index <= publicationHtmlContent.length; index++) {
			const publication = publicationHtmlContent[index - 1];
			publicationsHtmlContent += publication;
			var clearfix = "";
			if (index % inSmall == 0) {
				clearfix += " visible-sm";
			}
			if (index % inMed == 0) {
				clearfix += " visible-md";
			}
			if (index % inLarge == 0) {
				clearfix += " visible-lg";
			}
			if (clearfix !== "") {
				publicationsHtmlContent += "<div class=\"clearfix" + clearfix + "\"></div>";
			}
		}

		$publicationsContainer = $("#publications");
		$publicationsContainer.empty();
		$publicationsContainer.html(publicationsHtmlContent);
	});

	$.getJSON("json/people.json", people => {

		var peopleTemplate = _.template(" \
			<div class=\"col-xs-12 col-sm-6 col-md-3 col-lg-3 text-center topReveal\"> \
				<div class=\"team-member-box-2\"> \
					<div class=\"team-image-wrapper rotateTopReveal\"> \
						<a target=\"_blank\" href=\"<%= website %>\"> \
							<img src=\"<%= image %>\" alt=\"<%= name %>\" class=\"img-responsive img-circle team-member-img text-center\"> \
						</a> \
					</div> \
					<h3><%= name %></h3> \
					<p class=\"mb15\"><%= position %></p> \
				</div> \
			</div> \
		");

		var categoryTemplate = _.template(" \
			<h2 class=\"text-center mt40 mb40\"> <%= hidden ? '<a style=\"cursor: pointer; user-select: none;\" class=\"people-toggle\" data-shown=\"false\" id=\"people-toggle-'+id+'\">' : '' %> <%= name %>  <%= hidden ? '</a>' : '' %> </h2> \
			<div id=\"section-people-toggle-<%= id %>\" class=\"row <%= hidden ? 'people-hidden' : '' %>\"> \
				<%= content %> \
			</div> \
		");

		var peopleHtmlContent = people.categories
			.map(category => {
				var content = people.people.filter(person => person.category == category.id)

				content = content
					.sort((a, b) => {
						function lastName(person) {
							names = person.name.split(" ");
							return names[names.length - 1];
						}

						function prefix(person) {
							if (person.position.toLowerCase().includes("postdoc")) {
								return "A";
							} else if (person.position.toLowerCase().includes("phd")) {
								return "B";
							} else {
								return "C";
							}
						}

						return (prefix(a) + lastName(a)).localeCompare(prefix(b) + lastName(b));
					})
					.map(person => peopleTemplate(person));

				category.content = "";

				const inXSmall = 1;
				const inSmall = 2;
				const inMed = 4;
				const inLarge = 4;
				for (let index = 1; index <= content.length; index++) {
					const person = content[index - 1];
					category.content += person;
					var clearfix = "";
					if (index % inXSmall == 0) {
						clearfix += " visible-xs";
					}
					if (index % inSmall == 0) {
						clearfix += " visible-sm";
					}
					if (index % inMed == 0) {
						clearfix += " visible-md";
					}
					if (index % inLarge == 0) {
						clearfix += " visible-lg";
					}
					if (clearfix !== "") {
						category.content += "<div class=\"clearfix" + clearfix + "\"></div>";
					}
				}

				return categoryTemplate(category)
			})
			.reduce((accum, self) => accum + self);

		$peopleContainer = $("#people");
		$peopleContainer.empty();
		$peopleContainer.html(peopleHtmlContent);

		$(".people-toggle").click(
			function () {
				var id = $(this).attr('id');
				if ($(this).data('shown') === "true") {
					$(this).data('shown', "false");
					$("#section-" + id).hide();
				} else {
					$(this).data('shown', "true");
					$("#section-" + id).show();
				}
			}
		);
		$(".people-hidden").hide();
	});
});
