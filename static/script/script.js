// add class navbarDark on navbar scroll
const header = document.querySelector('.navbar');
console.log(header)
window.onscroll = function() {
    const top = window.scrollY;
    if(top >=100) {
        header.classList.add('navbarDark');
    }
    else {
        header.classList.remove('navbarDark');
    }
}
// collapse navbar after click on small devices
const navLinks = document.querySelectorAll('.nav-item')
const menuToggle = document.getElementById('navbarSupportedContent')
const btn = document.querySelector('.navbar-toggler')

function clickHandler() {
    header.classList.toggle('navbarLight');
}
function activateButton(button) {
    button.addEventListener('click', clickHandler);
}
function disableButton(button) { 
    button.removeEventListener('click', clickHandler);
}

activateButton(btn);

navLinks.forEach((l) => {
    l.addEventListener('click', () => { new bootstrap.Collapse(menuToggle).toggle() })
})