/* =========================================
   AL-KHWARIZMI SMART LIBRARY
   ULTRA MODERN HOME PAGE JS
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    initializeParticles();
    initializeRevealAnimations();
    initializeCounterAnimations();
    initializeNavbarEffects();
    initializeMouseEffects();
    initializeTiltEffects();
    initializeFloatingIcons();
    initializeParallax();
    initializeSearchEffects();

});

/* =========================================
   PARTICLES SYSTEM
========================================= */

function initializeParticles(){

    const particlesContainer =
        document.querySelector(".hero-particles");

    if(!particlesContainer) return;

    for(let i = 0; i < 60; i++){

        const particle =
            document.createElement("span");

        particle.classList.add("particle");

        const size =
            Math.random() * 6 + 2;

        particle.style.width =
            `${size}px`;

        particle.style.height =
            `${size}px`;

        particle.style.left =
            `${Math.random() * 100}%`;

        particle.style.top =
            `${Math.random() * 100}%`;

        particle.style.animationDuration =
            `${Math.random() * 12 + 8}s`;

        particle.style.animationDelay =
            `${Math.random() * 6}s`;

        particle.style.opacity =
            Math.random() * 0.6;

        particlesContainer.appendChild(particle);

    }

}

/* =========================================
   REVEAL ANIMATIONS
========================================= */

function initializeRevealAnimations(){

    const elements =
        document.querySelectorAll(
            ".modern-section, .ai-card, .modern-category-card, .book-card, .section-top"
        );

    elements.forEach((element) => {

        element.style.opacity = "0";
        element.style.transform = "translateY(60px)";
        element.style.transition =
            "all 1s cubic-bezier(.2,.65,.3,1)";

    });

    const observer =
        new IntersectionObserver((entries) => {

            entries.forEach((entry) => {

                if(entry.isIntersecting){

                    entry.target.style.opacity = "1";
                    entry.target.style.transform =
                        "translateY(0px)";

                }

            });

        }, {
            threshold:0.12
        });

    elements.forEach((element) => {

        observer.observe(element);

    });

}

/* =========================================
   COUNTER ANIMATION
========================================= */

function initializeCounterAnimations(){

    const counters =
        document.querySelectorAll(
            ".stat-counter"
        );

    counters.forEach((counter) => {

        const target =
            parseInt(counter.innerText) || 0;

        if (target === 0) return;

        let current = 0;

        const increment =
            Math.ceil(target / 70) || 1;

        const updateCounter = () => {

            current += increment;

            if(current >= target){

                counter.innerText = target;
                return;

            }

            counter.innerText = current;

            requestAnimationFrame(updateCounter);

        };

        updateCounter();

    });

}

/* =========================================
   NAVBAR EFFECT
========================================= */

function initializeNavbarEffects(){

    const navbar =
        document.querySelector(".navbar");

    if(!navbar) return;

    window.addEventListener("scroll", () => {

        if(window.scrollY > 40){

            navbar.style.background =
                "rgba(255,255,255,0.92)";

            navbar.style.backdropFilter =
                "blur(18px)";

            navbar.style.boxShadow =
                "0 10px 40px rgba(0,0,0,0.06)";

        }else{

            navbar.style.background =
                "rgba(255,255,255,0.85)";

            navbar.style.boxShadow =
                "none";

        }

    });

}

/* =========================================
   HERO MOUSE GLOW
========================================= */

function initializeMouseEffects(){

    const hero =
        document.querySelector(".hero-modern");

    if(!hero) return;

    const glow =
        document.createElement("div");

    glow.classList.add("mouse-glow");

    glow.style.position = "absolute";
    glow.style.width = "450px";
    glow.style.height = "450px";
    glow.style.borderRadius = "50%";
    glow.style.background =
        "radial-gradient(circle, rgba(37,99,235,0.22), transparent 70%)";

    glow.style.pointerEvents = "none";
    glow.style.filter = "blur(40px)";
    glow.style.zIndex = "1";
    glow.style.transition =
        "transform 0.08s linear";

    hero.appendChild(glow);

    hero.addEventListener("mousemove", (e) => {

        const rect =
            hero.getBoundingClientRect();

        const x =
            e.clientX - rect.left;

        const y =
            e.clientY - rect.top;

        glow.style.left =
            `${x - 225}px`;

        glow.style.top =
            `${y - 225}px`;

    });

}

/* =========================================
   3D TILT EFFECTS
========================================= */

function initializeTiltEffects(){

    const tiltElements =
        document.querySelectorAll(
            ".dashboard-preview, .floating-book-card, .home-hero-stat, .ai-card"
        );

    tiltElements.forEach((card) => {

        card.addEventListener("mousemove", (e) => {

            const rect =
                card.getBoundingClientRect();

            const x =
                e.clientX - rect.left;

            const y =
                e.clientY - rect.top;

            const centerX =
                rect.width / 2;

            const centerY =
                rect.height / 2;

            const rotateX =
                (y - centerY) / 18;

            const rotateY =
                (centerX - x) / 18;

            card.style.transform =
                `
                perspective(1000px)
                rotateX(${rotateX}deg)
                rotateY(${rotateY}deg)
                translateY(-8px)
                scale(1.02)
                `;

        });

        card.addEventListener("mouseleave", () => {

            card.style.transform = "";

        });

    });

}

/* =========================================
   FLOATING ICONS
========================================= */

function initializeFloatingIcons(){

    const icons =
        document.querySelectorAll(
            ".floating-icon"
        );

    icons.forEach((icon, index) => {

        setInterval(() => {

            const randomX =
                Math.random() * 20 - 10;

            const randomY =
                Math.random() * 20 - 10;

            icon.style.transform =
                `translate(${randomX}px, ${randomY}px)`;

        }, 3500 + index * 500);

    });

}

/* =========================================
   PARALLAX EFFECT
========================================= */

function initializeParallax(){

    window.addEventListener("scroll", () => {

        const scrollY =
            window.scrollY;

        const hero =
            document.querySelector(".hero-modern");

        const dashboard =
            document.querySelector(".dashboard-preview");

        const floatingBook =
            document.querySelector(".floating-book-card");

        if(hero){

            hero.style.backgroundPositionY =
                `${scrollY * 0.35}px`;

        }

        if(dashboard){

            dashboard.style.transform =
                `translateY(${scrollY * 0.04}px)`;

        }

        if(floatingBook){

            floatingBook.style.transform =
                `translateY(${scrollY * -0.05}px)`;

        }

    });

}

/* =========================================
   SEARCH EFFECTS
========================================= */

function initializeSearchEffects(){

    const search =
        document.querySelector(".home-hero-search");

    const input =
        document.querySelector(".home-hero-search input");

    if(!search || !input) return;

    input.addEventListener("focus", () => {

        search.style.transform =
            "translateY(-4px) scale(1.01)";

        search.style.boxShadow =
            "0 30px 60px rgba(37,99,235,0.25)";

        search.style.border =
            "1px solid rgba(255, 255, 255, 0.35)";

    });

    input.addEventListener("blur", () => {

        search.style.transform =
            "translateY(0px) scale(1)";

        search.style.boxShadow =
            "0 20px 45px rgba(0, 0, 0, 0.25)";

        search.style.border =
            "1px solid rgba(255, 255, 255, 0.22)";

    });

}

/* =========================================
   BUTTON RIPPLE EFFECT
========================================= */

const buttons =
    document.querySelectorAll(
        ".btn-modern, .hero-search-btn"
    );

buttons.forEach((button) => {

    button.addEventListener("click", function(e){

        const ripple =
            document.createElement("span");

        ripple.classList.add("ripple");

        const rect =
            button.getBoundingClientRect();

        const size =
            Math.max(rect.width, rect.height);

        ripple.style.width =
            ripple.style.height =
            `${size}px`;

        ripple.style.left =
            `${e.clientX - rect.left - size / 2}px`;

        ripple.style.top =
            `${e.clientY - rect.top - size / 2}px`;

        ripple.style.position = "absolute";
        ripple.style.borderRadius = "50%";
        ripple.style.background =
            "rgba(255,255,255,0.4)";

        ripple.style.transform = "scale(0)";
        ripple.style.animation =
            "ripple-animation 0.6s linear";

        ripple.style.pointerEvents = "none";

        button.appendChild(ripple);

        setTimeout(() => {

            ripple.remove();

        }, 600);

    });

});

/* =========================================
   RIPPLE STYLE
========================================= */

const rippleStyle =
document.createElement("style");

rippleStyle.innerHTML = `

@keyframes ripple-animation{

    to{
        transform:scale(4);
        opacity:0;
    }

}

.btn-modern,
.hero-search-btn{
    position:relative;
    overflow:hidden;
}

`;

document.head.appendChild(rippleStyle);

/* =========================================
   HERO TEXT ANIMATION
========================================= */

const heroTitle =
    document.querySelector(".hero-title span");

if(heroTitle){

    heroTitle.style.opacity = "0";
    heroTitle.style.transform =
        "translateY(40px)";

    setTimeout(() => {

        heroTitle.style.transition =
            "all 1.2s ease";

        heroTitle.style.opacity = "1";

        heroTitle.style.transform =
            "translateY(0px)";

    }, 500);

}

/* =========================================
   BOOK CARD HOVER LIGHT
========================================= */

const cards =
    document.querySelectorAll(".book-card");

cards.forEach((card) => {

    card.addEventListener("mousemove", (e) => {

        const rect =
            card.getBoundingClientRect();

        const x =
            e.clientX - rect.left;

        const y =
            e.clientY - rect.top;

        card.style.background =
            `
            radial-gradient(
                circle at ${x}px ${y}px,
                rgba(255,255,255,0.16),
                rgba(255,255,255,0.04)
            )
            `;

    });

    card.addEventListener("mouseleave", () => {

        card.style.background = "";

    });

});

/* =========================================
   PAGE LOADER
========================================= */

window.addEventListener("load", () => {

    document.body.classList.add("page-loaded");

});

/* =========================================
   SMOOTH SCROLL
========================================= */

document.querySelectorAll('a[href^="#"]')
.forEach((anchor) => {

    anchor.addEventListener("click", function(e){

        e.preventDefault();

        const target =
            document.querySelector(
                this.getAttribute("href")
            );

        if(target){

            target.scrollIntoView({
                behavior:"smooth",
                block:"start"
            });

        }

    });

});