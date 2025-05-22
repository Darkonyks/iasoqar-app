/**
 * IAF-EAC Primary - Funkcionalnost za postavljanje primarnog IAF/EAC koda
 * Deo reorganizacije frontend koda ISOQAR aplikacije
 */

(function($) {
    'use strict';
    
    // Inicijalizacija funkcionalnosti
    function initPrimaryIafEacHandler() {
        console.log('Inicijalizacija handlera za primarni IAF/EAC kod...');
        
        // Dodavanje event listenera za promenu primarnog IAF/EAC koda
        $(document).on('click', '.set-primary-iaf-eac-btn', function(e) {
            e.preventDefault();
            handleSetPrimaryIafEac($(this));
        });
    }
    
    // Funkcija za rukovanje postavljanjem primarnog IAF/EAC koda
    function handleSetPrimaryIafEac($button) {
        var codeId = $button.data('code-id');
        var codeName = $button.data('code-name');
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        
        if (!codeId) {
            console.error('Nedostaje ID za IAF/EAC kod');
            return;
        }
        
        console.log('Postavljanje IAF/EAC koda kao primarnog:', codeId, codeName);
        
        // Prikaz indikatora učitavanja
        $button.html('<i class="fas fa-spinner fa-spin"></i>');
        $button.prop('disabled', true);
        
        // Slanje AJAX zahteva
        $.ajax({
            url: '/company/api/iaf-eac/update-primary/',
            type: 'POST',
            data: {
                'code_id': codeId,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                console.log('IAF/EAC kod uspešno postavljen kao primarni:', response);
                
                // Prikaži poruku o uspehu
                if (typeof window.showDirectModal === 'function') {
                    window.showDirectModal(
                        'Primarni IAF/EAC kod ažuriran',
                        response.message,
                        'success'
                    );
                    
                    // Osveži stranicu nakon zatvaranja
                    setTimeout(function() {
                        window.location.reload();
                    }, 1500);
                } else {
                    alert(response.message);
                    window.location.reload();
                }
            },
            error: function(xhr, status, error) {
                console.error('Greška pri ažuriranju primarnog IAF/EAC koda:', error);
                
                // Resetovanje stanja dugmeta
                $button.html('<i class="fas fa-star"></i> Postavi kao primarni');
                $button.prop('disabled', false);
                
                // Priprema poruke o grešci
                var errorMessage = 'Došlo je do greške pri ažuriranju primarnog IAF/EAC koda.';
                
                try {
                    var response = JSON.parse(xhr.responseText);
                    if (response.message) {
                        errorMessage = response.message;
                    }
                } catch (e) {
                    // Ako nije moguće parsirati odgovor, koristi generičku poruku
                }
                
                // Prikaži poruku o grešci
                if (typeof window.showDirectModal === 'function') {
                    window.showDirectModal(
                        'Greška pri ažuriranju primarnog IAF/EAC koda',
                        errorMessage,
                        'error'
                    );
                } else {
                    alert(errorMessage);
                }
            }
        });
    }
    
    // Pokretanje inicijalizacije kada je dokument spreman
    $(document).ready(function() {
        initPrimaryIafEacHandler();
    });
    
})(jQuery);
