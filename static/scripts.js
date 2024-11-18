// Example of form validation or animation
document.addEventListener('DOMContentLoaded', function() {
    const button = document.querySelector('button');
    button.addEventListener('mouseover', function() {
        button.style.backgroundColor = '#45a049'; // Change color on hover
    });

    button.addEventListener('mouseout', function() {
        button.style.backgroundColor = '#4CAF50'; // Revert to original color
    });
});
// Sticky Navbar and Active Menu Link on Scroll
window.onscroll = function() {
    let navbar = document.querySelector('.navbar');
    if (window.pageYOffset > 50) {
        navbar.classList.add("sticky");
    } else {
        navbar.classList.remove("sticky");
    }

    let links = document.querySelectorAll('.navbar ul li a');
    links.forEach(link => {
        link.classList.remove('active');
        if (window.location.href.includes(link.getAttribute('href'))) {
            link.classList.add('active');
        }
    });
};