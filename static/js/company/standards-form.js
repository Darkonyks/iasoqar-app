/**
 * JavaScript za upravljanje formama za standarde kompanije
 * 
 * Deo reorganizacije frontend koda ISOQAR aplikacije
 */

(function($) {
    'use strict';
    
    // Kada je dokument spreman
    $(document).ready(function() {
        console.log('Inicijalizacija funkcionalnosti formi za standarde...');
        
        // Form validator za dodavanje standarda
        $('#standardAddForm').on('submit', function(e) {
            console.log('Pokrenuta validacija forme za dodavanje standarda');
            
            // Prikupljanje podataka
            var standardDefinition = $('#standard_definition').val();
            var formAction = $(this).attr('action');
            var companyId = formAction.match(/\/companies\/(\d+)\/standards\/add/)[1];
            
            console.log('Detalji forme:', {
                'form_action': formAction,
                'company_id': companyId,
                'standard_definition': standardDefinition,
                'issue_date': $('#issue_date').val(),
                'expiry_date': $('#expiry_date').val(),
                'notes': $('#notes').val()
            });
            
            // Validacija standarda
            if (!standardDefinition) {
                e.preventDefault();
                alert('Morate izabrati standard!');
                $('#standard_definition').focus();
                return false;
            }
            
            // Opciona validacija datuma
            var issueDate = $('#issue_date').val();
            var expiryDate = $('#expiry_date').val();
            
            if (issueDate && expiryDate) {
                var issueDateObj = new Date(issueDate);
                var expiryDateObj = new Date(expiryDate);
                
                if (expiryDateObj < issueDateObj) {
                    e.preventDefault();
                    alert('Datum isteka ne može biti pre datuma izdavanja!');
                    $('#expiry_date').focus();
                    return false;
                }
            }
            
            // Direktniji pristup - opciono
            if (confirm('Da li želite da dodate novi standard? Forma će biti poslata na ' + formAction)) {
                console.log('Korisnik je potvrdio slanje forme. Forma za dodavanje standarda je validna, prosleđujem...');
                return true;
            } else {
                e.preventDefault();
                console.log('Korisnik je otkazao slanje forme.');
                return false;
            }
        });
        
        // Omogući Bootstrap popovers za dodatne informacije
        $('[data-toggle="popover"]').popover();
        
        // Inicijalizacija Select2 za dropdown elemente ako je dostupan
        if ($.fn.select2) {
            $('#standard_definition').select2({
                placeholder: "Izaberite standard",
                allowClear: true,
                width: '100%'
            });
        }
    });
    
})(jQuery);
