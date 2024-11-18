// Form button hover effect
document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.btn-primary');
    buttons.forEach(button => {
        button.addEventListener('mouseover', function() {
            button.style.backgroundColor = '#45a049'; // Hover color
        });

        button.addEventListener('mouseout', function() {
            button.style.backgroundColor = '#28a745'; // Original color
        });
    });
});

// Sticky Navbar
window.onscroll = function() {
    let navbar = document.querySelector('.navbar');
    if (window.pageYOffset > 50) {
        navbar.classList.add("sticky");
    } else {
        navbar.classList.remove("sticky");
    }
};
// Animation for Input Fields
document.addEventListener("DOMContentLoaded", function() {
    const inputs = document.querySelectorAll(".input-field");

    inputs.forEach((input) => {
        input.addEventListener("focus", function() {
            input.style.boxShadow = "0 0 8px rgba(0, 123, 255, 0.3)";
        });
        input.addEventListener("blur", function() {
            input.style.boxShadow = "none";
        });
    });

    // Button Hover Animation
    const button = document.querySelector(".btn-login");
    button.addEventListener("mouseover", function() {
        button.style.transform = "translateY(-3px)";
        button.style.boxShadow = "0 4px 15px rgba(0, 91, 187, 0.3)";
    });
    button.addEventListener("mouseout", function() {
        button.style.transform = "translateY(0)";
        button.style.boxShadow = "none";
    });
});