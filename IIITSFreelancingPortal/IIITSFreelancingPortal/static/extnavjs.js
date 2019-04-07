const trigger = document.querySelector('.mobile-trigger');
const navbarLinks = document.querySelector('nav ul');
trigger.addEventListener('click', ()=> {
  trigger.classList.toggle('active');
	navbarLinks.classList.toggle('active');
 });