/**
 * Register funkcionalnosti
 * Deo reorganizacije frontend koda ISOQAR aplikacije
 */

(function($) {
    'use strict';
    
    // Inicijalizacija kada je dokument spreman
    $(document).ready(function() {
        console.log('Inicijalizacija register stranice...');
        
        // Validacija forme pre slanja
        $('form').on('submit', function(e) {
            var username = $('input[name="username"]').val();
            var password1 = $('input[name="password1"]').val();
            var password2 = $('input[name="password2"]').val();
            var agreeTerms = $('#agreeTerms').is(':checked');
            
            // Validacija polja
            if (!username || !password1 || !password2) {
                e.preventDefault();
                showValidationError('Molimo popunite sva polja.');
                return false;
            }
            
            // Validacija lozinki
            if (password1 !== password2) {
                e.preventDefault();
                showValidationError('Lozinke se ne podudaraju.');
                return false;
            }
            
            // Validacija uslova korišćenja
            if (!agreeTerms) {
                e.preventDefault();
                showValidationError('Morate prihvatiti uslove korišćenja.');
                return false;
            }
            
            return true;
        });
    });
    
    // Funkcija za prikazivanje grešaka validacije
    function showValidationError(message) {
        // Proveri da li već postoji poruka o grešci
        if ($('.alert-danger').length) {
            $('.alert-danger').html(message);
        } else {
            // Kreiraj novi element za poruku
            var alert = $('<div class="alert alert-danger alert-dismissible">' +
                          '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' +
                          message +
                          '</div>');
            
            // Dodaj poruku na početak forme
            $('form').prepend(alert);
        }
    }
    
})(jQuery);
