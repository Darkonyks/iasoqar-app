/**
 * IAF-EAC Handler - Objedinjeni modul za rukovanje IAF/EAC kodovima
 * Deo reorganizacije frontend koda ISOQAR aplikacije
 */

(function($) {
    'use strict';
    
    // Inicijalizacija
    $(document).ready(function() {
        console.log('Inicijalizacija IAF/EAC handlera...');
        initAddButton();
        initDeleteButtons();
        initPrimaryButtons();
    });
    
    // Inicijalizacija dugmeta za dodavanje
    function initAddButton() {
        $('#addIafEacButton').on('click', function(e) {
            e.preventDefault();
            var $btn = $(this);
            var companyId = $btn.data('company-id');
            
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
                    
                    // Poruka o grešci
                    var errorMsg = 'Došlo je do greške pri dodavanju IAF/EAC koda.';
                    if (xhr.status) {
                        errorMsg += ' (Status kod: ' + xhr.status + ')';
                    }
                    
                    showMessage('Greška pri dodavanju IAF/EAC koda', errorMsg, 'error');
                }
            });
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
        if (typeof window.showDirectModal === 'function') {
            window.showDirectModal(title, message, type);
        } else {
            alert(message);
        }
    }
    
})(jQuery);
