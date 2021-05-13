// Saves today's date
let today = new Date().toISOString().substr(0, 10);

// HTML hidden fields holding package information
let hours = document.querySelector("#hours");
let price = document.querySelector("#price");

// Sets todays date in modal on page load
document.addEventListener('DOMContentLoaded', setTodaysDateModal());

// Functions to set the modal fields for each class package
document.querySelector('#buy1').onclick = function() {
    setModalFields(1);
};
document.querySelector('#buy4').onclick = function() {
    setModalFields(4);
};
document.querySelector('#buy8').onclick = function() {
    setModalFields(8);
};

// Updates expiry date when user changes the start date of the package
document.querySelector('#start_date').onchange = function () {
    updateExpiryDate();
    validateForm();
};

// Sets the package start date to today's date
function setTodaysDateModal() {
    document.querySelector("#start_date").value = today;
}

// Sets hours, price and expiry date fields in modal
function setModalFields(packageHours){
    setTodaysDateModal();
    setModalHiddenFields(packageHours);
    updateExpiryDate();
}

function setModalHiddenFields(packageHours) {
    hours.value = packageHours;
    price.value = packageInfo[packageHours].price;
}

// This function updates the expiry date in the modal window based on the package
function updateExpiryDate() {

    // Ensures that expiry date is appropriately updated each time user changes hour package
    let days = packageInfo[`${hours.value}`].expiry;

    // Takes start date from the form + calculates expiry date
    var startDate = new Date(document.getElementById('start_date').value);
    var expiryDate = new Date(startDate.setDate(startDate.getDate() + days));

    // Converts it to appropriate format to put in the form
    document.getElementById('expirydate').value = expiryDate.toISOString().substr(0, 10);

    // Generate relevant label for the expiry date
    var text;
    if (days == 1) {
        text = `Your package will expire <strong>1 day</strong> after your start date:`;
    }
    else {
        text = `Your package will expire <strong>${days} days</strong> after your start date:`;
    }
    document.querySelector("#expiryLabel").innerHTML = text;
}

function validateForm() {
  var x = document.forms["startdate"]["start_date"].value;
  if (x < today) {
    alert("Date must be after today's date");
    return false;
  }
}

// triggers modal
$('#staticBackdrop').on('shown.bs.modal', function () {
    $('#modal').trigger('focus');
});