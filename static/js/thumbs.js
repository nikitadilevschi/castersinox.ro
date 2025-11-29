function changeMainImage(thumbnail) {
    const mainImage = document.getElementById('mainImage');
    const thumbnails = document.querySelectorAll('.thumbnail-images .owl-item');

    // Update main image
    mainImage.src = thumbnail.src;
    mainImage.alt = thumbnail.alt;

    // Remove active class from all items
    thumbnails.forEach(item => item.classList.remove('active'));

    // Add active class to clicked thumbnail's parent
    thumbnail.closest('.owl-item').classList.add('active');
}

// Document ready
$(document).ready(function() {
    // Initialize Owl Carousel
    const owl = $('#thumbnail').owlCarousel({
        items: 5,
        margin: 5,
        nav: false,
        dots: true,
        loop: false,
        autoplay: true,
        responsive: {
            0: {
                items: 2
            },
            480: {
                items: 3
            },
            768: {
                items: 3
            },
            1024: {
                items: 3
            }
        },
    });

    // Custom navigation buttons
    $('#prev-button').click(function() {
        owl.trigger('prev.owl.carousel');
    });

    $('#next-button').click(function() {
        owl.trigger('next.owl.carousel');
    });

    // Zoom effect for main image
    const zoomEffect = document.querySelector('.zoom-effect');
    const mainImage = document.querySelector('#mainImage');

    if (zoomEffect && mainImage) {
        zoomEffect.addEventListener('mousemove', (e) => {
            const bounds = zoomEffect.getBoundingClientRect();
            const x = e.clientX - bounds.left;
            const y = e.clientY - bounds.top;

            const zoomX = (x / bounds.width) * 100;
            const zoomY = (y / bounds.height) * 100;

            mainImage.style.transformOrigin = `${zoomX}% ${zoomY}%`;
        });

        zoomEffect.addEventListener('mouseleave', () => {
            mainImage.style.transformOrigin = 'center center';
        });
    }
});