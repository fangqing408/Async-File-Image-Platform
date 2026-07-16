function handleNavClick(event, el) {
    event.preventDefault();

    const targetId = el.getAttribute("data-target");
    const targetEl = document.getElementById(targetId);

    if (targetEl) {
        targetEl.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }

    const nav = document.querySelector('nav');
    if (nav.classList.contains('active')) {
        nav.classList.remove('active');
    }
}

function handleNavClick2(event, el) {
    const targetId = el.getAttribute("data-target");
    const targetEl = document.getElementById(targetId);

    if (targetEl) {
        targetEl.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }

    const nav = document.querySelector('nav');
    if (nav.classList.contains('active')) {
        nav.classList.remove('active');
    }
}

function updateActiveNav(el) {
    const navLinks = document.querySelectorAll("nav ul li a[data-target]");

    navLinks.forEach(link => {
        link.classList.remove("active");
    });

    el.classList.add('active');
}

function toggleMenu() {
    const nav = document.querySelector('nav');
    const hamburgerMenu = document.querySelector('.hamburger-menu');

    nav.classList.toggle('active');
    hamburgerMenu.classList.toggle('active');
}

function toggleDropdown(event) {
    event.preventDefault();
    const dropdown = event.target.closest('a').nextElementSibling;
    dropdown.classList.toggle('show');

    document.querySelectorAll('.dropdown-content').forEach(function(content) {
        if (content !== dropdown) {
            content.classList.remove('show');
        }
    });
}

function updateScrollHighlight() {
    const sections = document.querySelectorAll("section");
    const navLinks = document.querySelectorAll("nav ul li a[data-target]");

    let currentId = "hero";

    sections.forEach(section => {
        const rect = section.getBoundingClientRect();
        if (rect.top <= 100 && rect.bottom > 100) {
            currentId = section.id;
        }
    });

    navLinks.forEach(link => {
        if (link.getAttribute("data-target") === currentId) {
            link.classList.add("active");
        } else {
            link.classList.remove("active");
        }
    });
}

window.addEventListener("scroll", updateScrollHighlight);
window.addEventListener("load", updateScrollHighlight);

window.addEventListener("scroll", function() {
    let navbar = document.querySelector("header");
    let currentScroll = window.pageYOffset || document.documentElement.scrollTop;

    if (currentScroll > 50) {
        navbar.classList.add("scrolled");
    } else {
        navbar.classList.remove("scrolled");
    }
});

function createScrollIndicator() {
    const hero = document.querySelector('.hero');
    if (!hero) return;

    const indicator = document.createElement('div');
    indicator.className = 'scroll-indicator';
    indicator.innerHTML = '<span></span>';
    hero.appendChild(indicator);
}

document.addEventListener('DOMContentLoaded', createScrollIndicator);