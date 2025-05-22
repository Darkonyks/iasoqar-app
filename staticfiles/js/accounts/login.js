/**
 * Login funkcionalnosti
 * Deo reorganizacije frontend koda ISOQAR aplikacije
 */

(function($) {
    'use strict';
    
    // Inicijalizacija kada je dokument spreman
    $(document).ready(function() {
        console.log('Inicijalizacija login stranice...');
        
        // Validacija forme pre slanja
        $('form').on('submit', function(e) {
            var username = $('input[name="username"]').val();
            var password = $('input[name="password"]').val();
            
            if (!username || !password) {
                e.preventDefault();
                showValidationError('Molimo popunite sva polja.');
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
