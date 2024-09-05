//console.log('Welcome To Fotasco Security');
let email;
let phone;

document.getElementById("login1").textContent = 'Welcome To Fotasco Security';
document.getElementById("paragraph").textContent = 'Please select a category below';
document.getElementById("admin001").addEventListener("click", redirect)
function redirect(){ window.location = "http://127.0.0.1:5500/login.html"; }
document.getElementById("staff001").addEventListener("click", redirect)
function redirect(){ window.location = "http://127.0.0.1:5500/login.html"; }


const form = document.querySelector("form");
eField = form.querySelector(".email"),
eInput = eField.querySelector("input"),
pField = form.querySelector(".password"),
pInput = pField.querySelector("input");