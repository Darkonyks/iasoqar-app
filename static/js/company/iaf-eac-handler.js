/**
 * IAF-EAC Handler - Objedinjeni modul za rukovanje IAF/EAC kodovima
 * Deo reorganizacije frontend koda ISOQAR aplikacije
 */

(function($) {
    'use strict';
    
    // Inicijalizacija
    $(document).ready(function() {
        console.log('Inicijalizacija IAF/EAC handlera...');
        console.log('Provera da li postoji dugme za dodavanje:', $('#addIafEacButton').length);
        console.log('Provera da li je showDirectModal funkcija dostupna:', typeof window.showDirectModal === 'function');
        
        // Provera da li je csrfToken dostupan
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        console.log('CSRF token dostupan:', csrfToken ? 'Da' : 'Ne');
        
        initAddButton();
        initDeleteButtons();
        initPrimaryButtons();
    });
    
    // Inicijalizacija dugmeta za dodavanje
    function initAddButton() {
        console.log('Inicijalizacija dugmeta za dodavanje IAF/EAC koda...');
        
        // Direktno dodavanje event listenera umesto jQuery metode
        var addButton = document.getElementById('addIafEacButton');
        if (addButton) {
            console.log('Dodavanje click event listenera na dugme...');
            addButton.addEventListener('click', handleAddButtonClick);
        } else {
            console.error('Dugme za dodavanje IAF/EAC koda nije pronađeno u DOM-u!');
        }
        
        // Dodavanje i putem jQuery za svaki slučaj
        $('#addIafEacButton').on('click', function(e) {
            console.log('jQuery onClick handler za addIafEacButton aktiviran!');
            e.preventDefault();
            handleAddButtonClick(e);
        });
    }
    
    // Handler funkcija za klik na dugme za dodavanje
    function handleAddButtonClick(e) {
        console.log('Kliknuto je dugme za dodavanje IAF/EAC koda!', e);
        if (e && e.preventDefault) e.preventDefault();
        
        var $btn = $('#addIafEacButton');
        var companyId = $btn.data('company-id');
        console.log('ID kompanije:', companyId);
        
        // Validacija
        var iafEacCodeId = $('#iaf_eac_code_select').val();
        if (!iafEacCodeId) {
            showMessage('Potrebna validacija', 'Morate izabrati IAF/EAC kod pre nego što nastavite.', 'warning');
            $('#iaf_eac_code_select').focus();
            return;
        }
        
        // Prikupljanje podataka
        var notes = $('#iaf_eac_code_notes').val();
        var isPrimary = $('#iaf_eac_is_primary').is(':checked');
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        
        // Kreiranje relativne putanje (koristimo različite opcije da osiguramo da će jedna raditi)
        var baseUrl = window.location.pathname.includes('/companies/') ? '' : '/company';
        var url = baseUrl + '/companies/' + companyId + '/iaf-eac/add/';
        var data = {
            'iaf_eac_code': iafEacCodeId,
            'notes': notes,
            'is_primary': isPrimary,
            'csrfmiddlewaretoken': csrfToken
        };
        
        // UI ažuriranje
        var originalBtnText = $btn.html();
        $btn.html('<i class="fas fa-spinner fa-spin"></i> Dodajem...');
        $btn.prop('disabled', true);
        
        // AJAX poziv
        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            success: function(response) {
                // Čišćenje forme
                $('#iaf_eac_code_select').val('');
                $('#iaf_eac_code_notes').val('');
                $('#iaf_eac_is_primary').prop('checked', false);
                
                // Poruka o uspehu
                var codeName = $('#iaf_eac_code_select option:selected').text() || 'Odabrani kod';
                showMessage('IAF/EAC kod uspešno dodat', 
                            'IAF/EAC kod "' + codeName + '" je uspešno dodat kompaniji!', 
                            'success');
                
                // Osvežavanje stranice
                setTimeout(function() {
                    window.location.reload();
                }, 1500);
            },
            error: function(xhr, status, error) {
                // Resetovanje dugmeta
                $btn.html(originalBtnText);
                $btn.prop('disabled', false);
                
                console.log('AJAX greška za URL ' + url + ':', error);
                console.log('Status kod:', xhr.status);
                
                // Provera da li je operacija zapravo uspela uprkos status kodu 400
                // Ovo je specifična provera za slučaj kada server vrati 400 ali je kod ipak uspešno dodat
                if (xhr.status === 400) {
                    try {
                        var response = JSON.parse(xhr.responseText);
                        
                        // Ako odgovor sadrži grešku o već postojećem kodu, to znači da je kod zapravo sačuvan
                        if (response && response.error && response.error.includes('već ima dodeljen ovaj IAF/EAC kod')) {
                            // Obradi kao uspeh - kod je zapravo dodat u bazu
                            var codeName = $('#iaf_eac_code_select option:selected').text() || 'Odabrani kod';
                            showMessage('IAF/EAC kod je već dodat', 
                                       'Ovaj IAF/EAC kod je već dodeljen kompaniji.',
                                       'info');
                            
                            // Čišćenje forme
                            $('#iaf_eac_code_select').val('');
                            $('#iaf_eac_code_notes').val('');
                            $('#iaf_eac_is_primary').prop('checked', false);
                            
                            return;
                        }
                    } catch (e) {
                        console.error('Greška pri parsiranju JSON odgovora:', e);
                    }
                }
                
                // Standardna obrada greške ako nije prepoznat uspeh
                var errorMessage = 'Došlo je do greške pri dodavanju IAF/EAC koda.';
                if (xhr.status) {
                    errorMessage += ' (Status kod: ' + xhr.status + ')';
                }
                
                // Pokušaj izvlačenja detaljnije poruke o grešci
                try {
                    var response = JSON.parse(xhr.responseText);
                    if (response && response.error) {
                        errorMessage += '\n\nDetalji: ' + response.error;
                    }
                } catch (e) {
                    console.error('Greška pri parsiranju JSON odgovora:', e);
                }
                
                showMessage('Greška pri dodavanju IAF/EAC koda', 
                           errorMessage, 
                           'error');
            }
        });
    }
    
    // Inicijalizacija dugmeta za brisanje
    function initDeleteButtons() {
        $(document).on('click', '.delete-iaf-eac-btn', function(e) {
            e.preventDefault();
            var codeId = $(this).data('code-id');
            var codeName = $(this).data('code-name');
            
            if (confirm('Da li ste sigurni da želite da obrišete IAF/EAC kod "' + codeName + '"?')) {
                var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
                
                $.ajax({
                    url: (window.location.pathname.includes('/companies/') ? '' : '/company') + '/api/iaf-eac/delete/',
                    type: 'POST',
                    data: {
                        'code_id': codeId,
                        'csrfmiddlewaretoken': csrfToken
                    },
                    success: function(response) {
                        showMessage('IAF/EAC kod obrisan', 
                                   'IAF/EAC kod "' + codeName + '" je uspešno obrisan.', 
                                   'success');
                        
                        setTimeout(function() {
                            window.location.reload();
                        }, 1500);
                    },
                    error: function(xhr, status, error) {
                        showMessage('Greška pri brisanju IAF/EAC koda', 
                                   'Došlo je do greške pri brisanju IAF/EAC koda.', 
                                   'error');
                    }
                });
            }
        });
    }
    
    // Inicijalizacija dugmeta za postavljanje primarnog koda
    function initPrimaryButtons() {
        $(document).on('click', '.set-primary-iaf-eac-btn', function(e) {
            e.preventDefault();
            var codeId = $(this).data('code-id');
            var codeName = $(this).data('code-name');
            var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
            
            // UI ažuriranje
            var $btn = $(this);
            $btn.html('<i class="fas fa-spinner fa-spin"></i>');
            $btn.prop('disabled', true);
            
            $.ajax({
                url: (window.location.pathname.includes('/companies/') ? '' : '/company') + '/api/iaf-eac/update-primary/',
                type: 'POST',
                data: {
                    'code_id': codeId,
                    'csrfmiddlewaretoken': csrfToken
                },
                success: function(response) {
                    showMessage('Primarni IAF/EAC kod ažuriran', 
                               'IAF/EAC kod "' + codeName + '" je postavljen kao primarni.', 
                               'success');
                    
                    setTimeout(function() {
                        window.location.reload();
                    }, 1500);
                },
                error: function(xhr, status, error) {
                    // Resetovanje dugmeta
                    $btn.html('<i class="fas fa-star"></i>');
                    $btn.prop('disabled', false);
                    
                    showMessage('Greška pri ažuriranju primarnog IAF/EAC koda', 
                               'Došlo je do greške pri ažuriranju primarnog IAF/EAC koda.', 
                               'error');
                }
            });
        });
    }
    
    // Pomoćna funkcija za prikazivanje poruka
    function showMessage(title, message, type) {
        console.log('Pozivanje showMessage funkcije:', title, message, type);
        console.log('showDirectModal funkcija dostupna:', typeof window.showDirectModal === 'function');
        
        if (typeof window.showDirectModal === 'function') {
            console.log('Pokušaj prikazivanja direktnog modala...');
            try {
                window.showDirectModal(title, message, type);
                console.log('Direktni modal uspešno prikazan');
            } catch (error) {
                console.error('Greška pri prikazivanju direktnog modala:', error);
                alert(title + '\n\n' + message);
            }
        } else {
            console.log('Prikazivanje alert poruke umesto modala');
            alert(message);
        }
    }
    
})(jQuery);
