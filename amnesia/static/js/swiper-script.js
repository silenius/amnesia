jQuery(document).ready(function($) {
                    
                    var swiper = new Swiper('.swiper-container', {
                        effect: 'coverflow',
                        grabCursor: true,
                        centeredSlides: true,
                        paginationClickable: false,
                        nextButton: '.swiper-button-next',
                        prevButton: '.swiper-button-prev',
                        slidesPerView: 5,
                        spaceBetween: 30,
                        speed: 800,
                        loop: true,
                        autoplay: true,
                        autoplayDisableOnInteraction: true,
                        coverflow: {
                            rotate: 50,
                            stretch: 0,
                            depth: 100,
                            modifier: 1,
                            slideShadows : true
                        },
                        // Responsive breakpoints
                        breakpoints: {
                            // when window width is <= 1024px
                            1024: {
                              slidesPerView: 1,
                              spaceBetweenSlides: 10
                            }
                        }
                    });
                    swiper.slideTo(2, 800, true);
                    $('.swiper-button-prev').one('click', function(event) {
                        event.preventDefault();
                        swiper.slideTo(1, 800, true);
                    });

                    $('.swiper-button-next').one('click', function(event) {
                        event.preventDefault();
                        swiper.slideTo(3, 800, true);
                    });
                });
                
