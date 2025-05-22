/**
 * Standards Validation - Funkcionalnost za validaciju standarda
 * Deo reorganizacije frontend koda ISOQAR aplikacije
 */

(function($) {
    'use strict';
    
    // Funkcija za prikazivanje validacionog modala - korišćenje direktnog modala
    function showValidationModal(message) {
        console.log('Prikazujem validacioni modal sa direktnim pristupom:', message);
        
        // Koristimo naš novi direktni modal umesto Bootstrap modala
        if (typeof window.showDirectModal === 'function') {
            window.showDirectModal(
                'Potrebna validacija', // Naslov
                message || 'Morate ispravno popuniti sva obavezna polja.', // Poruka
                'warning' // Tip (warning, success, error, info)
            );
        } else {
            // Fallback na standardni alert ako direktni modal nije dostupan
            console.error('Direktni modal nije dostupan!');
            alert(message || 'Morate ispravno popuniti sva obavezna polja.');
        }
    }
    
    // Inicijalizacija nakon učitavanja dokumenta
    $(document).ready(function() {
        console.log('Inicijalizacija validacije standarda...');
        
        // Zamenjujemo standardni alert sa lepim modalom
        $('#directStandardAdd').on('click', function(e) {
            e.preventDefault();
            
            var standardDefinition = $('#standard_definition').val();
            
            // Validacija standarda
            if (!standardDefinition) {
                showValidationModal('Morate izabrati standard pre nego što nastavite.');
                
                // Fokusiraj select polje kada se modal zatvori
                $('#standardValidationModal').on('hidden.bs.modal', function() {
                    $('#standard_definition').focus();
                });
                
                return false;
            }
            
            // Nastavi sa ostatkom logike iz standards-add.js
            var companyId = $(this).data('company-id');
            var addUrl = '/company/companies/' + companyId + '/standards/add/';
            
            // Prikupljanje podataka iz forme
            var formData = {
                'standard_definition': standardDefinition,
                'issue_date': $('#issue_date').val(),
                'expiry_date': $('#expiry_date').val(),
                'notes': $('#notes').val(),
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            };
            
            // Validacija datuma
            if (formData.issue_date && formData.expiry_date) {
                var issueDateObj = new Date(formData.issue_date);
                var expiryDateObj = new Date(formData.expiry_date);
                
                if (expiryDateObj < issueDateObj) {
                    showValidationModal('Datum isteka ne može biti pre datuma izdavanja!');
                    
                    // Fokusiraj polje datuma isteka kada se modal zatvori
                    $('#standardValidationModal').on('hidden.bs.modal', function() {
                        $('#expiry_date').focus();
                    });
                    
                    return false;
                }
            }
            
            console.log('Direktno dodavanje standarda!');
            console.log('URL:', addUrl);
            console.log('Podaci:', formData);
            
            // Prikaz indikatora učitavanja na dugmetu
            var $btn = $(this);
            var originalBtnText = $btn.html();
            $btn.html('<i class="fas fa-spinner fa-spin"></i> Dodajem...');
            $btn.prop('disabled', true);
            
            // Slanje AJAX zahteva
            $.ajax({
                url: addUrl,
                type: 'POST',
                data: formData,
                success: function(response) {
                    console.log('Standard uspešno dodat pomoću direktnog dugmeta!');
                    
                    // Resetovanje forme - sigurniji pristup
                    if ($('#standardAddForm').length > 0) {
                        $('#standardAddForm')[0].reset();
                    } else {
                        // Resetuj polja pojedinačno ako forma nije dostupna
                        $('#standard_definition').val('');
                        $('#issue_date').val('');
                        $('#expiry_date').val('');
                        $('#notes').val('');
                    }
                    
                    // Dohvati naziv dodatog standarda
                    var standardName = $('#standard_definition option:selected').text();
                    
                    // Pripremi i prikaži direktni modal za uspešno dodavanje
                    if (typeof window.showDirectModal === 'function') {
                        window.showDirectModal(
                            'Standard uspešno dodat', // Naslov
                            'Standard "' + standardName + '" je uspešno dodat u sistem!', // Poruka
                            'success' // Tip (success)
                        );
                        
                        // Osveži stranicu nakon 1.5 sekunde
                        setTimeout(function() {
                            window.location.reload();
                        }, 1500);
                    } else {
                        // Fallback ako direktni modal nije dostupan
                        alert('Standard "' + standardName + '" je uspešno dodat!');
                        window.location.reload();
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Greška pri direktnom dodavanju standarda:', error);
                    console.error('Status:', xhr.status);
                    console.error('Odgovor:', xhr.responseText);
                    
                    // Resetovanje stanja dugmeta
                    $btn.html(originalBtnText);
                    $btn.prop('disabled', false);
                    
                    // Priprema teksta greške za prikaz
                    var errorMessage = 'Došlo je do greške pri dodavanju standarda.';
                    try {
                        var responseObj = JSON.parse(xhr.responseText);
                        if (responseObj.error) {
                            errorMessage += '\n\nPoruka: ' + responseObj.error;
                        }
                    } catch (e) {
                        if (xhr.responseText && xhr.responseText.length < 200) {
                            errorMessage += '\n\nDetalji: ' + xhr.responseText;
                        } else {
                            errorMessage += '\n\nStatus kod: ' + xhr.status;
                        }
                    }
                    
                    // Prikaži grešku koristeći direktni modal
                    if (typeof window.showDirectModal === 'function') {
                        window.showDirectModal(
                            'Greška pri dodavanju standarda', // Naslov
                            errorMessage, // Poruka
                            'error' // Tip (error)
                        );
                    } else {
                        // Fallback na alert ako direktni modal nije dostupan
                        alert(errorMessage);
                    }
                }
            });
        });
    });
    
    // Eksportujemo funkciju za korišćenje u drugim modulima
    window.showStandardValidationModal = showValidationModal;
    
})(jQuery);
