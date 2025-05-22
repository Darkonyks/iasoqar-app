/**
 * IAF-EAC Add - Direktno dodavanje IAF/EAC kodova
 * Deo reorganizacije frontend koda ISOQAR aplikacije
 */

(function($) {
    'use strict';
    
    // Glavna funkcija za inicijalizaciju
    function initIafEacAdd() {
        console.log('Inicijalizacija direktnog dodavanja IAF/EAC koda...');
        
        // Zakačimo event handler na dugme za dodavanje IAF/EAC koda
        $('#addIafEacButton').on('click', function(e) {
            e.preventDefault();
            handleIafEacAdd(this);
        });
    }
    
    // Funkcija koja obrađuje direktno dodavanje IAF/EAC koda
    function handleIafEacAdd(buttonElement) {
        // Prikupljanje podataka iz forme
        var iafEacCodeId = $('#iaf_eac_code_select').val();
        var notes = $('#iaf_eac_code_notes').val();
        var isPrimary = $('#iaf_eac_is_primary').is(':checked');
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        
        // Validacija IAF/EAC koda
        if (!iafEacCodeId) {
            // Prikaži validacioni modal
            if (typeof window.showDirectModal === 'function') {
                window.showDirectModal(
                    'Potrebna validacija',
                    'Morate izabrati IAF/EAC kod pre nego što nastavite.',
                    'warning'
                );
            } else {
                alert('Morate izabrati IAF/EAC kod!');
            }
            $('#iaf_eac_code_select').focus();
            return false;
        }
        
        // Prikupljanje URL-a i Company ID-a iz atributa dugmeta
        var $btn = $(buttonElement);
        var companyId = $btn.data('company-id');
        
        // Generisanje mogućih URL putanja
        var possibleUrls = [
            '/company/companies/' + companyId + '/iaf-eac/add/',
            '/companies/' + companyId + '/iaf-eac/add/',
            '/api/iaf-eac/add/' + companyId + '/'
        ];
        
        // Prikaz indikatora učitavanja na dugmetu
        var originalBtnText = $btn.html();
        $btn.html('<i class="fas fa-spinner fa-spin"></i> Dodajem...');
        $btn.prop('disabled', true);
        
        // Formiranje podataka za slanje
        var formData = {
            'iaf_eac_code': iafEacCodeId,
            'notes': notes,
            'is_primary': isPrimary,
            'csrfmiddlewaretoken': csrfToken
        };
        
        console.log('Direktno dodavanje IAF/EAC koda...');
        console.log('Mogući URL-ovi:', possibleUrls);
        console.log('Podaci:', formData);
        
        // Pokušaj sa prvim URL-om
        tryUrl(0);
        
        // Funkcija koja rekurzivno pokušava URL-ove
        function tryUrl(urlIndex) {
            if (urlIndex >= possibleUrls.length) {
                // Ako smo isprobali sve URL-ove i ništa nije uspelo, prikaži grešku
                console.error('Svi pokušaji URL-ova su neuspešni');
                handleError({
                    status: 404,
                    statusText: 'Not Found',
                    responseText: 'Svi pokušaji za dodavanje IAF/EAC koda su neuspešni. URL nije pronađen.'
                });
                return;
            }
            
            var currentUrl = possibleUrls[urlIndex];
            console.log('Pokušavam URL:', currentUrl, '(Pokušaj ' + (urlIndex + 1) + ' od ' + possibleUrls.length + ')');
            
            $.ajax({
                url: currentUrl,
                type: 'POST',
                data: formData,
                success: function(response) {
                    console.log('IAF/EAC kod uspešno dodat!', response);
                    
                    // Čišćenje polja forme
                    $('#iaf_eac_code_select').val('');
                    $('#iaf_eac_code_notes').val('');
                    $('#iaf_eac_is_primary').prop('checked', false);
                    
                    // Dohvati naziv dodatog koda za prikaz poruke
                    var codeName = $('#iaf_eac_code_select option:selected').text() || 'Odabrani kod';
                    
                    // Prikaži modal za uspeh
                    if (typeof window.showDirectModal === 'function') {
                        window.showDirectModal(
                            'IAF/EAC kod uspešno dodat',
                            'IAF/EAC kod "' + codeName + '" je uspešno dodat kompaniji!',
                            'success'
                        );
                        
                        // Osveži stranicu nakon zatvaranja
                        setTimeout(function() {
                            window.location.reload();
                        }, 1500);
                    } else {
                        alert('IAF/EAC kod uspešno dodat!');
                        window.location.reload();
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Greška sa URL-om ' + currentUrl + ':', error);
                    console.error('Status:', xhr.status);
                    
                    // Pokušaj sledeći URL
                    tryUrl(urlIndex + 1);
                }
            });
        }
        
        // Funkcija za rukovanje greškom nakon što su svi URL-ovi isprobani
        function handleError(xhr) {
            console.error('Finalna greška pri dodavanju IAF/EAC koda:', xhr);
            
            // Resetovanje stanja dugmeta
            $btn.html(originalBtnText);
            $btn.prop('disabled', false);
            
            // Priprema poruke o grešci
            var errorMessage = 'Došlo je do greške pri dodavanju IAF/EAC koda.';
            
            // Pokušaj parsirati odgovor
            try {
                if (xhr.responseText) {
                    var response = JSON.parse(xhr.responseText);
                    if (response.error) {
                        errorMessage += '\n\nDetalji: ' + response.error;
                    }
                }
            } catch (e) {
                if (xhr.status) {
                    errorMessage += '\n\nStatus kod: ' + xhr.status;
                }
                if (xhr.statusText) {
                    errorMessage += ' (' + xhr.statusText + ')';
                }
                if (xhr.responseText && xhr.responseText.length < 200) {
                    errorMessage += '\n\nOdgovor: ' + xhr.responseText;
                }
            }
            
            // Prikaži grešku
            if (typeof window.showDirectModal === 'function') {
                window.showDirectModal(
                    'Greška pri dodavanju IAF/EAC koda',
                    errorMessage,
                    'error'
                );
            } else {
                alert(errorMessage);
            }
        }
    }
    
    // Pokretanje inicijalizacije kada je dokument spreman
    $(document).ready(function() {
        initIafEacAdd();
    });
    
})(jQuery);

(function($) {
    'use strict';
    
    // Glavna funkcija za inicijalizaciju
    function initIafEacAdd() {
        console.log('Inicijalizacija direktnog dodavanja IAF/EAC koda...');
        
        // Zakačimo event handler na dugme za dodavanje IAF/EAC koda
        $('#addIafEacButton').on('click', function(e) {
            e.preventDefault();
            handleIafEacAdd(this);
        });
    }
    
    // Funkcija koja obrađuje direktno dodavanje IAF/EAC koda
    function handleIafEacAdd(buttonElement) {
        // Prikupljanje podataka iz forme
        var iafEacCodeId = $('#iaf_eac_code_select').val();
        var notes = $('#iaf_eac_code_notes').val();
        var isPrimary = $('#iaf_eac_is_primary').is(':checked');
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        
        // Validacija IAF/EAC koda
        if (!iafEacCodeId) {
            // Prikaži validacioni modal
            if (typeof window.showDirectModal === 'function') {
                window.showDirectModal(
                    'Potrebna validacija',
                    'Morate izabrati IAF/EAC kod pre nego što nastavite.',
                    'warning'
                );
            } else {
                alert('Morate izabrati IAF/EAC kod!');
            }
            $('#iaf_eac_code_select').focus();
            return false;
        }
        
        // Prikupljanje URL-a i Company ID-a iz atributa dugmeta
        var $btn = $(buttonElement);
        var companyId = $btn.data('company-id');
        
        // Generisanje mogućih URL putanja
        var possibleUrls = [
            '/company/companies/' + companyId + '/iaf-eac/add/',
            '/companies/' + companyId + '/iaf-eac/add/',
            '/api/iaf-eac/add/' + companyId + '/'
        ];
        
        // Prikaz indikatora učitavanja na dugmetu
        var originalBtnText = $btn.html();
        $btn.html('<i class="fas fa-spinner fa-spin"></i> Dodajem...');
        $btn.prop('disabled', true);
        
        // Formiranje podataka za slanje
        var formData = {
            'iaf_eac_code': iafEacCodeId,
            'notes': notes,
            'is_primary': isPrimary,
            'csrfmiddlewaretoken': csrfToken
        };
        
        console.log('Direktno dodavanje IAF/EAC koda...');
        console.log('Mogući URL-ovi:', possibleUrls);
        console.log('Podaci:', formData);
        
        // Pokušaj sa prvim URL-om
        tryUrl(0);
        
        // Funkcija koja rekurzivno pokušava URL-ove
        function tryUrl(urlIndex) {
            if (urlIndex >= possibleUrls.length) {
                // Ako smo isprobali sve URL-ove i ništa nije uspelo, prikaži grešku
                console.error('Svi pokušaji URL-ova su neuspešni');
                handleError({
                    status: 404,
                    statusText: 'Not Found',
                    responseText: 'Svi pokušaji za dodavanje IAF/EAC koda su neuspešni. URL nije pronađen.'
                });
                return;
            }
            
            var currentUrl = possibleUrls[urlIndex];
            console.log('Pokušavam URL:', currentUrl, '(Pokušaj ' + (urlIndex + 1) + ' od ' + possibleUrls.length + ')');
            
            $.ajax({
                url: currentUrl,
                type: 'POST',
                data: formData,
                success: function(response) {
                    console.log('IAF/EAC kod uspešno dodat!', response);
                    
                    // Čišćenje polja forme
                    $('#iaf_eac_code_select').val('');
                    $('#iaf_eac_code_notes').val('');
                    $('#iaf_eac_is_primary').prop('checked', false);
                    
                    // Dohvati naziv dodatog koda za prikaz poruke
                    var codeName = $('#iaf_eac_code_select option:selected').text() || 'Odabrani kod';
                    
                    // Prikaži modal za uspeh
                    if (typeof window.showDirectModal === 'function') {
                        window.showDirectModal(
                            'IAF/EAC kod uspešno dodat',
                            'IAF/EAC kod "' + codeName + '" je uspešno dodat kompaniji!',
                            'success'
                        );
                        
                        // Osveži stranicu nakon zatvaranja
                        setTimeout(function() {
                            window.location.reload();
                        }, 1500);
                    } else {
                        alert('IAF/EAC kod uspešno dodat!');
                        window.location.reload();
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Greška sa URL-om ' + currentUrl + ':', error);
                    console.error('Status:', xhr.status);
                    
                    // Pokušaj sledeći URL
                    tryUrl(urlIndex + 1);
                }
            });
        }
        
        // Funkcija za rukovanje greškom nakon što su svi URL-ovi isprobani
        function handleError(xhr) {
            console.error('Finalna greška pri dodavanju IAF/EAC koda:', xhr);
            
            // Resetovanje stanja dugmeta
            $btn.html(originalBtnText);
            $btn.prop('disabled', false);
            
            // Priprema poruke o grešci
            var errorMessage = 'Došlo je do greške pri dodavanju IAF/EAC koda.';
            
            // Pokušaj parsirati odgovor
            try {
                if (xhr.responseText) {
                    var response = JSON.parse(xhr.responseText);
                    if (response.error) {
                        errorMessage += '\n\nDetalji: ' + response.error;
                    }
                }
            } catch (e) {
                if (xhr.status) {
                    errorMessage += '\n\nStatus kod: ' + xhr.status;
                }
                if (xhr.statusText) {
                    errorMessage += ' (' + xhr.statusText + ')';
                }
                if (xhr.responseText && xhr.responseText.length < 200) {
                    errorMessage += '\n\nOdgovor: ' + xhr.responseText;
                }
            }
            
            // Prikaži grešku
            if (typeof window.showDirectModal === 'function') {
                window.showDirectModal(
                    'Greška pri dodavanju IAF/EAC koda',
                    errorMessage,
                    'error'
                );
            } else {
                alert(errorMessage);
            }
        }
    }
    
    // Pokretanje inicijalizacije kada je dokument spreman
    $(document).ready(function() {
        initIafEacAdd();
    });
    
})(jQuery);

(function($) {
    'use strict';
    
    // Glavna funkcija za inicijalizaciju
    function initIafEacAdd() {
        console.log('Inicijalizacija direktnog dodavanja IAF/EAC koda...');
        
        // Zakačimo event handler na dugme za dodavanje IAF/EAC koda
        $('#addIafEacButton').on('click', function(e) {
            e.preventDefault();
            handleIafEacAdd(this);
        });
    }
    
    // Funkcija koja obrađuje direktno dodavanje IAF/EAC koda
    function handleIafEacAdd(buttonElement) {
        // Prikupljanje podataka iz forme
        var iafEacCodeId = $('#iaf_eac_code_select').val();
        var notes = $('#iaf_eac_code_notes').val();
        var isPrimary = $('#iaf_eac_is_primary').is(':checked');
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        
        // Validacija IAF/EAC koda
        if (!iafEacCodeId) {
            // Prikaži validacioni modal
            if (typeof window.showDirectModal === 'function') {
                window.showDirectModal(
                    'Potrebna validacija',
                    'Morate izabrati IAF/EAC kod pre nego što nastavite.',
                    'warning'
                );
            } else {
                alert('Morate izabrati IAF/EAC kod!');
            }
            $('#iaf_eac_code_select').focus();
            return false;
        }
        
        // Prikupljanje URL-a i Company ID-a iz atributa dugmeta
        var $btn = $(buttonElement);
        var companyId = $btn.data('company-id');
        var addUrl = '/company/companies/' + companyId + '/iaf-eac/add/';
        
        // Detektujemo pravu putanju na osnovu trenutne lokacije
        var pathPatterns = [
            '/company/companies/' + companyId + '/iaf-eac/add/',  // Pun path sa /company/ prefiksom
            '/companies/' + companyId + '/iaf-eac/add/',          // Bez /company/ prefiksa
            '/company/api/iaf-eac/add/' + companyId + '/',       // Alternativna API putanja
        ];
        
        // Uzmemo osnovni URL aplikacije
        var baseUrl = window.location.origin;
        console.log('Osnovni URL:', baseUrl);
        
        // Koristi čest pattern za Django aplikacije 
        addUrl = '/company/companies/' + companyId + '/iaf-eac/add/';
        
        // Dodaj event za grešku koji će probati alternativne putanje ako prva ne radi
        var pathIndex = 0;
        
        // Funkcija za generisanje callback-a za alternativnu putanju
        window.tryAlternativePath = function() {
            pathIndex++;
            if (pathIndex < pathPatterns.length) {
                console.log('Probavanje alternativne putanje:', pathPatterns[pathIndex]);
                return pathPatterns[pathIndex];
            }
            return null;
        };
        
        // Formiranje podataka za slanje
        var formData = {
            'iaf_eac_code': iafEacCodeId,
            'notes': notes,
            'is_primary': isPrimary,
            'csrfmiddlewaretoken': csrfToken
        };
        
        console.log('Direktno dodavanje IAF/EAC koda...');
        console.log('URL:', addUrl);
        console.log('Podaci:', formData);
        
        // Prikaz indikatora učitavanja na dugmetu
        var originalBtnText = $btn.html();
        $btn.html('<i class="fas fa-spinner fa-spin"></i> Dodajem...');
        $btn.prop('disabled', true);
        
        // Funkcija za slanje AJAX zahteva koja će probati alternativne putanje ako prva ne uspe
        function sendAjaxRequest(url, retryCount) {
            console.log('Slanje AJAX zahteva na URL:', url, 'Preostalo pokušaja:', retryCount);
            
            $.ajax({
                url: url,
                type: 'POST',
                data: formData,
                success: function(response) {
                console.log('IAF/EAC kod uspešno dodat!', response);
                
                // Čišćenje polja forme
                $('#iaf_eac_code_select').val('');
                $('#iaf_eac_code_notes').val('');
                $('#iaf_eac_is_primary').prop('checked', false);
                
                // Dohvati naziv dodatog koda za prikaz poruke
                var codeName = $('#iaf_eac_code_select option:selected').text() || 'Odabrani kod';
                
                // Prikaži modal za uspeh
                if (typeof window.showDirectModal === 'function') {
                    window.showDirectModal(
                        'IAF/EAC kod uspešno dodat',
                        'IAF/EAC kod "' + codeName + '" je uspešno dodat kompaniji!',
                        'success'
                    );
                    
                    // Osveži stranicu nakon zatvaranja
                    setTimeout(function() {
                        window.location.reload();
                    }, 1500);
                } else {
                    alert('IAF/EAC kod uspešno dodat!');
                    window.location.reload();
                }
            },
            error: function(xhr, status, error) {
                console.error('Greška pri dodavanju IAF/EAC koda:', error);
                console.error('Status:', xhr.status);
                console.error('Odgovor:', xhr.responseText);
                
                // Resetovanje stanja dugmeta
                $btn.html(originalBtnText);
                $btn.prop('disabled', false);
                
                // Priprema poruke o grešci
                var errorMessage = 'Došlo je do greške pri dodavanju IAF/EAC koda.';
                
                // Pokušaj parsirati odgovor
                try {
                    if (xhr.responseText) {
                        var response = JSON.parse(xhr.responseText);
                        if (response.error) {
                            errorMessage += '\n\nDetalji: ' + response.error;
                        }
                    }
                } catch (e) {
                    if (xhr.status) {
                        errorMessage += '\n\nStatus kod: ' + xhr.status;
                    }
                }
                
                // Prikaži grešku
                if (typeof window.showDirectModal === 'function') {
                    window.showDirectModal(
                        'Greška pri dodavanju IAF/EAC koda',
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
        initIafEacAdd();
    });
    
})(jQuery);
