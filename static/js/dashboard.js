
var account_settings = document.getElementById("account-settings")
var account_usage= document.getElementById("account-usage")
var account_tokens = document.getElementById("account-tokens")
var account_billing = document.getElementById("account-billing")
var account_apps= document.getElementById("account-apps")



function unhideAccount(){
    account_settings.style.display = "block"
    account_usage.style.display = "none"
    account_tokens.style.display = "none"
    account_billing.style.display = "none"
    account_apps.style.display = "none"
}

function unhideUsage(){
    account_settings.style.display = "none"
    account_usage.style.display = "block"
    account_tokens.style.display = "none"
    account_billing.style.display = "none"
    account_apps.style.display = "none"
}

function unhideApps(){
    account_settings.style.display = "none"
    account_usage.style.display = "none"
    account_tokens.style.display = "none"
    account_billing.style.display = "none"
    account_apps.style.display = "block"
}

function unhideTokens(){
    account_settings.style.display = "none"
    account_usage.style.display = "none"
    account_tokens.style.display = "block"
    account_billing.style.display = "none"
    account_apps.style.display = "none"

}

function unhideBilling(){
    account_settings.style.display = "none"
    account_usage.style.display = "none"
    account_tokens.style.display = "none"
    account_billing.style.display = "block"
    account_apps.style.display = "none"

}

function togglePassword() {
    var x = document.getElementById("api-key-value");
    if (x.type === "password") {
    x.type = "text";
    } else {
    x.type = "password";
    }
}

new ClipboardJS('[data-clipboard-text]')

function copyPassword() {
    var passwordField = document.getElementById('api-key-value');
    var clipboardButton = document.querySelector('[data-clipboard-text]');

    clipboardButton.setAttribute('data-clipboard-text', passwordField.value);

    // Trigger the copy action
    clipboardButton.click();
}

document.addEventListener("clipboard-copy",() => {
    alert("Key copied to clipboard!")
})

document.getElementById("create-app-btn").addEventListener("click",() => {
    var app_form = document.getElementById("create-app-form")
    if(app_form.style.display == "none"){
        app_form.style.display = "block"
        document.getElementById("create-app-btn").innerHTML = `
        <i class="bi bi-x-lg"></i> Close
        `
    }else{
        app_form.style.display = "none"
        document.getElementById("create-app-btn").innerHTML = `
        <i class="bi bi-plus-circle-dotted"></i> Create App
        `
    }
})

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
}

var csrf = getCookie('csrftoken')
function createApp(){
    var app_name = document.getElementById("appname")
    $.ajax({
        type: 'POST',
        url: '/create-app/',
        data: {
            'csrfmiddlewaretoken': csrf,
            'app_name': app_name.value,
        },
        success: (res) => {
            if(res.error){
                const failNotification = document.getElementById('fail-notification');
                var failMessage = document.getElementById('fail-message');

                failMessage.innerText = res.error

                // Show the notification and animate it in from the right
                failNotification.classList.remove('hidden');
                failNotification.classList.add('animate');
            }else{
                if (document.getElementById("no-app") != null){
                    document.getElementById("no-app").style.display = "none"
                }
                document.getElementById("apps-wrapper").innerHTML += `
                <div class="max-w-sm w-full bg-white shadow-lg rounded-lg overflow-hidden">
                    <div class="px-4 py-2">
                    <h1 class="text-gray-900 font-bold text-2xl">${res.name}</h1>
                    <p class="text-gray-600 mt-2 text-sm">Description of App 1.</p>
                    </div>
                    <div class="px-4 py-2">
                    <a href="#" class="block text-center text-white bg-gray-800 py-2 px-4 rounded hover:bg-gray-700">View</a>
                    </div>
                </div>
            `
            const successNotification = document.getElementById('success-notification');
            var successMessage = document.getElementById('success-message');

            successMessage.innerText = res.data

            // Show the notification and animate it in from the right
            successNotification.classList.remove('hidden');
            successNotification.classList.add('animate');
            }  
        },
        error: (err) => {
            
        }
    })
}

function updateProfile(){
    var first_name = document.getElementById("first_name")
    var last_name = document.getElementById("last_name")
    var email = document.getElementById("email")
    
    $.ajax({
        type: 'POST',
        url: '/update-profile/',
        data: {
            'csrfmiddlewaretoken': csrf,
            'first_name': first_name.value,
            'last_name':last_name.value,
            'email':email.value,
        },
        success: (res) => {
            if(res.error){
                const failNotification = document.getElementById('fail-notification');
                var failMessage = document.getElementById('fail-message');

                failMessage.innerText = res.error

                // Show the notification and animate it in from the right
                failNotification.classList.remove('hidden');
                failNotification.classList.add('animate');
            }else{
                first_name.value = res.first_name
                last_name.value = res.last_name
                email.value = res.email

                const successNotification = document.getElementById('success-notification');
                var successMessage = document.getElementById('success-message');

                successMessage.innerText = res.data

                // Show the notification and animate it in from the right
                successNotification.classList.remove('hidden');
                successNotification.classList.add('animate');
            }  
        },
        error: (err) => {
            
        }
    })

}

const popup = document.getElementById('popup');
const popup_btn = document.getElementById('popup-btn');



function poupUpdateForm(){

    popup.classList.toggle("hidden")
    if (popup_btn.innerText == "Update Card"){
        popup_btn.innerText = "Close"
    }else{
        popup_btn.innerText = "Update Card"
    }
}

function sendUpdateCardForm(e){
    e.preventDefault();
    var card_number = document.getElementById("card_number")
    var expiration_date = document.getElementById("expiration_date")
    var cvc = document.getElementById("cvc")
    $.ajax({
        type: 'POST',
        url: '/update-card/',
        data: {
            'csrfmiddlewaretoken': csrf,
            'card_number': card_number.value,
            'expiration_date':expiration_date.value,
            'cvc':cvc.value,
        },
        success: (res) => {
            if(res.error){
                const failNotification = document.getElementById('fail-notification');
                var failMessage = document.getElementById('fail-message');

                failMessage.innerText = res.error

                // Show the notification and animate it in from the right
                failNotification.classList.remove('hidden');
                failNotification.classList.add('animate');
            }else{
            //    alert(res.data)
               const successNotification = document.getElementById('success-notification');
               var successMessage = document.getElementById('success-message');

               successMessage.innerText = res.data

               // Show the notification and animate it in from the right
                successNotification.classList.remove('hidden');
                successNotification.classList.add('animate');

            }  
        },
        error: (err) => {
            
        }
    })
}

var numberInput = document.getElementById("card_number")
var expiryInput = document.getElementById("expiration_date")
var cvvInput = document.getElementById("cvc")

// Card Number Input Formatting
numberInput.addEventListener('input', (e) => {
    const input = e.target.value.replace(/\D/g, '').substring(0,16);
    const cardType = getCardType(input);
    e.target.value = input.match(/.{1,4}/g)?.join(' ');
    e.target.parentElement.setAttribute('data-card-type', cardType);
});

// Expiration Date Input Formatting
expiryInput.addEventListener('input', (e) => {
    const input = e.target.value.replace(/\D/g, '').substring(0, 4);
    e.target.value = input.match(/.{1,2}/g)?.join('/');
});

// CVV Input Formatting
cvvInput.addEventListener('input', (e) => {
    const input = e.target.value.replace(/\D/g, '').substring(0, 3);
    e.target.value = input;
});
  
// Card Type Detection
function getCardType(input) {
    const visaRegEx = /^4[0-9]{12}(?:[0-9]{3})?$/;
    const mastercardRegEx = /^5[1-5][0-9]{14}$/;
    const amexRegEx = /^3[47][0-9]{13}$/;
    const discoverRegEx = /^6(?:011|5[0-9]{2})[0-9]{12}$/;

    if (visaRegEx.test(input)) {
        return 'visa';
    }

    if (mastercardRegEx.test(input)) {
        return 'mastercard';
    }

    if (amexRegEx.test(input)) {
        return 'amex';
    }

    if (discoverRegEx.test(input)) {
        return 'discover';
    }

    return 'unknown';
}

const successCloseNotification = document.getElementById('success-close-notification');
const failCloseNotification = document.getElementById('fail-close-notification');
const successNotification = document.getElementById('success-notification');
const failNotification = document.getElementById('fail-notification');

// Add an event listener to the close button to hide the notification and animate it out to the left
successCloseNotification.addEventListener('click', function() {
    successNotification.classList.remove('animate');
    successNotification.classList.add('hidden');
});
failCloseNotification.addEventListener('click', function() {
    failNotification.classList.remove('animate');
    failNotification.classList.add('hidden');
});


function deleteCard(){
    var result = confirm("If you delete the card, you will be automatically switch to Free plan. Do you want to delete?")
    if(result == true){
        $.ajax({
            type: 'POST',
            url: '/delete-card/',
            data: {
                'csrfmiddlewaretoken': csrf,
            },
            success: (res) => {
                if(res.error){
                    const failNotification = document.getElementById('fail-notification');
                    var failMessage = document.getElementById('fail-message');
    
                    failMessage.innerText = res.error
    
                    // Show the notification and animate it in from the right
                    failNotification.classList.remove('hidden');
                    failNotification.classList.add('animate');
                }else{
                //    alert(res.data)
                   const successNotification = document.getElementById('success-notification');
                   var successMessage = document.getElementById('success-message');
    
                   successMessage.innerText = res.data
    
                   // Show the notification and animate it in from the right
                    successNotification.classList.remove('hidden');
                    successNotification.classList.add('animate');
    
                }  
            },
            error: (err) => {
                
            }
        })
    }
}