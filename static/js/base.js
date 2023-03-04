handburger_menu = document.getElementById("handburger-menu")
mobile_menu = document.getElementById("mobile-menu")
close_btn = document.getElementById("close-btn")


handburger_menu.addEventListener("click", function (){
    mobile_menu.style.display = "block"
})

close_btn.addEventListener("click", function (){
    mobile_menu.style.display = "none"
})