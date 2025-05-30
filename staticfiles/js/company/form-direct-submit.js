/**
 * Direktni handler za formu - jednostavan i direktan pristup
 */

// Funkcija za debagovanje
function debugFormSubmit() {
    console.log('DEBUG FORM SUBMIT FUNCTION CALLED');
    
    // Pronađi formu i dugme
    var form = document.querySelector('form[method="post"]');
    var button = document.getElementById('saveCompanyButton');
    
    console.log('Form found:', !!form);
    console.log('Button found:', !!button);
    
    if (form && button) {
        // Prikaži poruku o uspehu
        alert('Pronašli smo formu i dugme! Pokušaćemo aktivirati slanje forme.');
        
        // Dodaj direktni event listener na dugme
        button.addEventListener('click', function(e) {
            console.log('DIREKTNO KLIKNUTO DUGME PREKO NOVOG LISTENERA');
            // Ne sprečavamo default akciju da bi forma bila poslata
        });
        
        // Dodaj direktni event listener na formu
        form.addEventListener('submit', function(e) {
            console.log('FORM SUBMIT EVENT TRIGGERED');
            console.log('Form action:', form.action);
            console.log('Form method:', form.method);
            
            // Ovde ne sprečavamo default akciju da bi forma bila poslata
        });
        
        console.log('Event listeneri su postavljeni na formu i dugme.');
    } else {
        console.error('Ne mogu pronaći formu ili dugme!');
        alert('Ne mogu pronaći formu ili dugme za čuvanje!');
    }
}

// Pozovi funkciju kada je dokument spreman
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM je učitan, postavljam direktne event listenere...');
    setTimeout(debugFormSubmit, 500); // Malo odložimo da budemo sigurni da je DOM učitan
});

// Pozovi i odmah za svaki slučaj
console.log('form-direct-submit.js je učitan');
debugFormSubmit();

// Postavi i globalni window.onload handler
window.onload = function() {
    console.log('Window je potpuno učitan, pokušavam ponovo...');
    debugFormSubmit();
};
