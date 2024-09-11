const form = document.querySelector("form"),
        nextBtn = form.querySelector(".nextBtn"),
      
        allInput = form.querySelectorAll(".first input");


nextBtn.addEventListener("click", ()=> {
    allInput.forEach(input => {
        if(input.value != ""){
            form.classList.add('secActive');
        }else{
            form.classList.remove('secActive');
        }
    })
})

let e = document.getElementById("role");
let strUser = e.options[e.selectedIndex].value;


backBtn.addEventListener("click", () => form.classList.remove('secActive'));