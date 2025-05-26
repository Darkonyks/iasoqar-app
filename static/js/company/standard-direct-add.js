/**
 * Standard Direct Add - Modul za direktno dodavanje standarda
 * Deo reorganizacije frontend koda ISOQAR aplikacije
 */

(function($) {
    'use strict';
    
    // Glavna funkcija za inicijalizaciju
    function initDirectStandardAdd() {
        console.log('Inicijalizacija direktnog dodavanja standarda...');
        
        // Zakačimo event handler na dugme
        $('#directStandardAdd').on('click', function(e) {
            e.preventDefault();
            handleDirectStandardAdd(this);
        });
    }
    
    // Funkcija koja obrađuje direktno dodavanje standarda
    function handleDirectStandardAdd(buttonElement) {
        // Prikupljanje podataka iz forme
        var standardDefinition = $('#standard_definition').val();
        var issueDate = $('#issue_date').val();
        var expiryDate = $('#expiry_date').val();
        var notes = $('#notes').val();
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        
        // Validacija standarda
        if (!standardDefinition) {
            // Prikaži validacioni modal
            if (typeof window.showDirectModal === 'function') {
                window.showDirectModal(
                    'Potrebna validacija',
                    'Morate izabrati standard pre nego što nastavite.',
                    'warning'
                );
            } else {
                alert('Morate izabrati standard!');
            }
            $('#standard_definition').focus();
            return false;
        }
        
        // Prikupljanje URL-a i Company ID-a iz atributa dugmeta
        var $btn = $(buttonElement);
        var companyId = $btn.data('company-id');
        var addUrl = '/company/companies/' + companyId + '/standards/add/';
        
        // Formiranje podataka za slanje
        var formData = {
            'standard_definition': standardDefinition,
            'issue_date': issueDate,
            'expiry_date': expiryDate,
            'notes': notes,
            'csrfmiddlewaretoken': csrfToken
        };
        
        console.log('Direktno dodavanje standarda...');
        console.log('URL:', addUrl);
        console.log('Podaci:', formData);
        
        // Prikaz indikatora učitavanja na dugmetu
        var originalBtnText = $btn.html();
        $btn.html('<i class="fas fa-spinner fa-spin"></i> Dodajem...');
        $btn.prop('disabled', true);
        
        // Slanje AJAX zahteva
        $.ajax({
            url: addUrl,
            type: 'POST',
            data: formData,
            success: function(response) {
                console.log('Standard uspešno dodat!', response);
                
                // Dohvati naziv dodatog standarda - sigurna verzija
                var standardName = '';
                try {
                    // Dohvati selektovanu opciju i njen tekst pre čišćenja forme
                    var selectedOption = $('#standard_definition option:selected');
                    standardName = selectedOption.text();
                    
                    // Dodatna provera da nije podrazumevana opcija
                    if (standardName === '-- Izaberite standard --') {
                        // Ako iz nekog razloga nije moguće dohvatiti pravi naziv, pokušaj sa response
                        if (response && response.standard_name) {
                            standardName = response.standard_name;
                        } else {
                            standardName = 'Odabrani standard';
                        }
                    }
                } catch (e) {
                    standardName = 'Standard';
                    console.error('Greška pri dohvatanju naziva standarda:', e);
                }
                
                // Čišćenje polja - ručno, bez resetovanja forme
                $('#standard_definition').val('');
                $('#issue_date').val('');
                $('#expiry_date').val('');
                $('#notes').val('');
                
                // Prikaži modal za uspeh
                if (typeof window.showDirectModal === 'function') {
                    window.showDirectModal(
                        'Standard uspešno dodat',
                        'Standard "' + standardName + '" je uspešno dodat u sistem!',
                        'success'
                    );
                    
                    // Osveži stranicu nakon zatvaranja
                    setTimeout(function() {
                        window.location.reload();
                    }, 1500);
                } else {
                    alert('Standard uspešno dodat!');
                    window.location.reload();
                }
            },
            error: function(xhr, status, error) {
                console.error('Greška pri dodavanju standarda:', error);
                console.error('Status:', xhr.status);
                console.error('Odgovor:', xhr.responseText);
                
                // Resetovanje stanja dugmeta
                $btn.html(originalBtnText);
                $btn.prop('disabled', false);
                
                // Priprema poruke o grešci
                var errorMessage = 'Došlo je do greške pri dodavanju standarda.';
                
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
                        'Greška pri dodavanju standarda',
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
        initDirectStandardAdd();
    });
    
})(jQuery);
