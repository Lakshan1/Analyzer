

// alert(document.querySelector("#submitBtn").dataset.lookupname)

var stripe

fetch("/config/")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  stripe = Stripe(data.publicKey);
});


function postData(e) {
  // Added below statement to prevent page reload for demo purposes - otherwise log value will disappear.
  e.preventDefault();
  const form = e.target;
  const data = new FormData(form);
  const object = {};
  data.forEach((value, key) => object[key] = value);
  
  fetch(`/create-checkout-session/${object['lookup_name']}/`)
        .then((result) => {
          return result.json();
        })
        .then((data) => {
          console.log(data);

          // Redirect to Stripe Checkout
          return stripe.redirectToCheckout({ sessionId: data.sessionId });
        })
        .catch((res) => {
          console.log(res);
        });
}

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

function changeSubscription(e,lookup_name){
  e.preventDefault()
  $.ajax({
    type: 'POST',
    url: '/change-subscription/',
    data: {
        'csrfmiddlewaretoken': csrf,
        'lookup_name': lookup_name,
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
