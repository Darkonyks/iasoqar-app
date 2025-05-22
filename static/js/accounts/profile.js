/**
 * Profile funkcionalnosti
 * Deo reorganizacije frontend koda ISOQAR aplikacije
 */

(function($) {
    'use strict';
    
    // Inicijalizacija kada je dokument spreman
    $(document).ready(function() {
        console.log('Inicijalizacija profile stranice...');
        
        // Inicijalizacija tabova
        initTabs();
        
        // Validacija forme za podešavanja
        $('#settings form').on('submit', function(e) {
            // Ovde možemo dodati dodatnu validaciju ako je potrebno
            return true;
        });
        
        // Validacija forme za promenu lozinke
        $('#password form').on('submit', function(e) {
            var currentPassword = $('#currentPassword').val();
            var newPassword = $('#newPassword').val();
            var confirmPassword = $('#confirmPassword').val();
            
            // Validacija polja
            if (!currentPassword || !newPassword || !confirmPassword) {
                e.preventDefault();
                showValidationError('Molimo popunite sva polja.');
                return false;
            }
            
            // Validacija lozinki
            if (newPassword !== confirmPassword) {
                e.preventDefault();
                showValidationError('Nova lozinka i potvrda lozinke se ne podudaraju.');
                return false;
            }
            
            return true;
        });
    });
    
    // Inicijalizacija tabova
    function initTabs() {
        // Zapamti aktivni tab između sesija
        var activeTab = localStorage.getItem('profileActiveTab');
        if (activeTab) {
            $('.nav-pills a[href="' + activeTab + '"]').tab('show');
        }
        
        // Postavi event listener za promenu taba
        $('.nav-pills a').on('shown.bs.tab', function(e) {
            var target = $(e.target).attr('href');
            localStorage.setItem('profileActiveTab', target);
        });
    }
    
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
            
            // Dodaj poruku na početak aktivne forme
            $('.tab-pane.active form').prepend(alert);
        }
    }
    
})(jQuery);
