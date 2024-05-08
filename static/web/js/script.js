(function ($) {
    "use strict";
    $(".offer-slider").slick({
        slidesToShow: 1,
        arrows: true,
        responsive: [
            { breakpoint: 768, settings: { arrows: true, centerMode: true, centerPadding: "40px", slidesToShow: 1 } },
            { breakpoint: 480, settings: { arrows: false, centerMode: true, centerPadding: "5px", slidesToShow: 1 } },
        ],
    });
    $(".banner-slider").slick({
        slidesToShow: 1,
        arrows: true,
        responsive: [
            { breakpoint: 768, settings: { arrows: true, centerMode: true, centerPadding: "40px", slidesToShow: 1 } },
            { breakpoint: 480, settings: { arrows: false, centerMode: true, centerPadding: "40px", slidesToShow: 1 } },
        ],
    });
    $(".cat-slider").slick({
        slidesToShow: 8,
        arrows: true,
        infinite: true,
        responsive: [
            { breakpoint: 768, settings: { arrows: true, centerMode: false, centerPadding: "40px", slidesToShow: 4 } },
            { breakpoint: 480, settings: { arrows: false, centerMode: false, centerPadding: "40px", slidesToShow: 4 } },
        ],
    });
    $(".trending-slider").slick({
        slidesToShow: 4,
        centerMode: false,
        arrows: true,
        responsive: [
            { breakpoint: 768, settings: { arrows: false, centerMode: false, centerPadding: "40px", slidesToShow: 2 } },
            { breakpoint: 480, settings: { arrows: false, centerMode: false, centerPadding: "40px", slidesToShow: 1 } },
        ],
    });
    $(".popular-slider").slick({
        centerMode: true,
        centerPadding: "30px",
        slidesToShow: 1,
        arrows: false,
        responsive: [
            { breakpoint: 768, settings: { arrows: false, centerMode: true, centerPadding: "40px", slidesToShow: 2 } },
            { breakpoint: 480, settings: { arrows: false, centerMode: true, centerPadding: "40px", slidesToShow: 1 } },
        ],
    });
    $(".osahan-slider").slick({ centerMode: false, slidesToShow: 1, arrows: false, dots: true });
    $(".osahan-slider-map").slick({
        autoplay: true,
        slidesToShow: 5,
        arrows: true,
        responsive: [
            { breakpoint: 768, settings: { arrows: false, autoplay: true, centerMode: true, centerPadding: "40px", slidesToShow: 3 } },
            { breakpoint: 480, settings: { arrows: false, autoplay: true, centerMode: true, centerPadding: "40px", slidesToShow: 3 } },
        ],
    });
    var $main_nav = $("#main-nav");
    var $toggle = $(".toggle");
    var defaultOptions = { disableAt: false, customToggle: $toggle, levelSpacing: 40, navTitle: "Askbootstrap", levelTitles: true, levelTitleAsBack: true, pushContent: "#container", insertClose: 2 };
    var Nav = $main_nav.hcOffcanvasNav(defaultOptions);

    // $('[data-bs-toggle="tooltip"]').tooltip();

    $('.portfolio-menu ul li').click(function () {
        $('.portfolio-menu ul li').removeClass('active');
        $(this).addClass('active');

        var selector = $(this).attr('data-filter');
        $('.portfolio-item').isotope({
            filter: selector
        });
        return false;
    });

    $(window).on('load', function () {
        $('.modal.fade').appendTo('body');
    })
    
})(jQuery);

