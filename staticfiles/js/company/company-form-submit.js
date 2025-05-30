/**
 * JavaScript za osposobljavanje funkcionalnosti dugmeta "Sačuvaj izmene"
 * Datoteka: company-form-submit.js
 */

(function($) {
    'use strict';
    
    // Inicijalno logovanje pri učitavanju skripte
    console.log('====== COMPANY FORM SUBMIT SCRIPT LOADED ======');
    
    // Funkcija koja se poziva kada je DOM učitan
    $(document).ready(function() {
        console.log('====== COMPANY FORM SUBMIT INIT STARTED ======');
        console.log('jQuery verzija:', $.fn.jquery);
        console.log('Document ready state:', document.readyState);
        
        // Debug informacije o formi i stranici
        console.log('URL stranice:', window.location.href);
        console.log('Sve forme na stranici:', $('form').length);
        console.log('Sve forme sa method="post":', $('form[method="post"]').length);
        console.log('Sva submit dugmad:', $('button[type="submit"]').length);
        
        // Pronalaženje forme i submit dugmeta - sada sa preciznijim selektorima
        const $form = $('form[method="post"]');
        const $submitButton = $form.find('button[type="submit"]');
        // Alternativni selektori ako prvi ne uspe
        const $submitButtonAll = $('button[type="submit"]');
        const $saveButton = $('button:contains("Sačuvaj")'); // Probamo naći po tekstu
        
        console.log('Pronađena forma:', $form.length ? 'DA' : 'NE', $form);
        console.log('Pronađeno submit dugme u formi:', $submitButton.length ? 'DA' : 'NE', $submitButton);
        console.log('Sva submit dugmad na stranici:', $submitButtonAll.length ? 'DA (' + $submitButtonAll.length + ')' : 'NE');
        console.log('Dugmad sa tekstom "Sačuvaj":', $saveButton.length ? 'DA (' + $saveButton.length + ')' : 'NE');
        
        // Koristićemo najbolji dostupni selektor
        let $buttonToUse = $submitButton.length ? $submitButton : 
                         ($submitButtonAll.length ? $submitButtonAll : 
                         ($saveButton.length ? $saveButton : null));
                         
        console.log('Dugme koje ćemo koristiti:', $buttonToUse);
        
        // Pomoćna funkcija za debug HTML-a
        function debugElementHTML(selector, name) {
            try {
                const $elements = $(selector);
                console.log(name + ' pronađeno:', $elements.length);
                $elements.each(function(i) {
                    console.log(name + ' #' + i + ' HTML:', $(this).prop('outerHTML'));
                });
            } catch(e) {
                console.error('Greška pri debug-u:', e);
            }
        }
        
        // Debug svih dugmadi na stranici
        debugElementHTML('button', 'Dugme');
        debugElementHTML('input[type="submit"]', 'Submit input');
        debugElementHTML('.btn-primary', 'Primary button');
        debugElementHTML('form .btn', 'Form button');
        
        if ($form.length === 0) {
            console.error('KRITIČNA GREŠKA: Forma nije pronađena na stranici!');
            alert('Greška: Forma nije pronađena!');
            return;
        }
        
        if (!$buttonToUse || $buttonToUse.length === 0) {
            console.error('KRITIČNA GREŠKA: Nijedno dugme za sačuvavanje nije pronađeno!');
            console.log('HTML forme:', $form.html());
            alert('Greška: Dugme za sačuvavanje nije pronađeno!');
            return;
        }
        
        // Logovanje atributa submit dugmeta
        console.log('Submit dugme tekst:', $buttonToUse.text());
        console.log('Submit dugme HTML:', $buttonToUse.prop('outerHTML'));
        console.log('Submit dugme klase:', $buttonToUse.attr('class'));
        console.log('Submit dugme tip:', $buttonToUse.attr('type'));
        
        console.log('Postavljanje event handlera za klik na submit dugme...');
        
        // Uklanjanje svih prethodnih event handlera sa dugmeta (za svaki slučaj)
        $buttonToUse.off('click');
        
        // Dodavanje novog event handlera - sa ispravljenim otkrivanjem događaja
        $buttonToUse.on('click', function(e) {
            // Obavezno zaustaviti propagaciju i default ponašanje
            e.preventDefault();
            e.stopPropagation();
            
            console.log('====== SAVE BUTTON CLICKED ======');
            console.log('Event objekat:', e);
            console.log('Event target:', e.target);
            console.log('This:', this);
            
            // Proverimo da li je forma još uvek validna
            console.log('Forma još uvek postoji:', $form.length);
            console.log('Submit dugme još uvek postoji:', $(this).length);
            
            try {
                console.log('Započinjem pripremu podataka za slanje...');
                
                // Priprema podataka pre slanja
                console.log('prepareIAFEACData funkcija postoji:', typeof window.prepareIAFEACData === 'function');
                console.log('prepareStandardsData funkcija postoji:', typeof window.prepareStandardsData === 'function');
                
                if (typeof window.prepareIAFEACData === 'function') {
                    console.log('Pozivam prepareIAFEACData...');
                    window.prepareIAFEACData();
                    console.log('prepareIAFEACData uspešno pozvana');
                } else if (typeof prepareIAFEACData === 'function') {
                    console.log('Pozivam lokalnu prepareIAFEACData...');
                    prepareIAFEACData();
                    console.log('Lokalna prepareIAFEACData uspešno pozvana');
                } else {
                    console.warn('Funkcija prepareIAFEACData nije pronađena!');
                }
                
                if (typeof window.prepareStandardsData === 'function') {
                    console.log('Pozivam prepareStandardsData...');
                    window.prepareStandardsData();
                    console.log('prepareStandardsData uspešno pozvana');
                } else if (typeof prepareStandardsData === 'function') {
                    console.log('Pozivam lokalnu prepareStandardsData...');
                    prepareStandardsData();
                    console.log('Lokalna prepareStandardsData uspešno pozvana');
                } else {
                    console.warn('Funkcija prepareStandardsData nije pronađena!');
                }
                
                // Validacija forme
                console.log('Počinjem validaciju forme...');
                const isValid = validateForm($form);
                console.log('Rezultat validacije forme:', isValid ? 'VALIDNA' : 'NIJE VALIDNA');
                
                if (isValid) {
                    console.log('Forma je validna, pripremam slanje...');
                    
                    // Pripremi vrednosti skrivenih polja za slanje
                    console.log('Vrednost #iaf_eac_codes_data:', $('#iaf_eac_codes_data').val());
                    console.log('Vrednost #standards_data:', $('#standards_data').val());
                    
                    // Proveri CSRF token
                    const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
                    console.log('CSRF token postoji:', !!csrfToken);
                    
                    // Prikaži loader
                    console.log('Prikazujem loader na dugmetu...');
                    showSubmitProgress($buttonToUse);
                    
                    // Direktno slanje forme - logujemo sve vrednosti polja
                    console.log('Vrednosti svih polja forme:');
                    $form.find('input, select, textarea').each(function() {
                        const $field = $(this);
                        console.log($field.attr('name') + ':', $field.val());
                    });
                    
                    console.log('ACTION URL forme:', $form.attr('action') || 'Default URL');
                    console.log('METHOD forme:', $form.attr('method'));
                    console.log('ENCODING TYPE forme:', $form.attr('enctype'));
                    
                    // Pokreni slanje forme
                    console.log('POKUŠAJ DIREKTNOG SLANJA FORME...');
                    $form.submit();
                    console.log('Submit funkcija je pozvana');
                    
                    // Backup metoda ako direktan submit ne radi
                    setTimeout(function() {
                        console.log('Pokušavam nativni submit kao fallback...');
                        try {
                            $form[0].submit();
                            console.log('Nativni submit je pozvan');
                        } catch (err) {
                            console.error('Greška pri nativnom submit-u:', err);
                        }
                    }, 500);
                } else {
                    console.error('Forma nije validna, otkazujem slanje.');
                    
                    // Prikaži grešku
                    console.log('showDirectModal funkcija postoji:', typeof window.showDirectModal === 'function');
                    if (typeof window.showDirectModal === 'function') {
                        console.log('Prikazujem modal grešku...');
                        window.showDirectModal(
                            'Greška pri čuvanju podataka',
                            'Molimo popunite sva obavezna polja pre čuvanja.',
                            'error'
                        );
                    } else {
                        console.log('Koristim alert za prikaz greške...');
                        alert('Molimo popunite sva obavezna polja pre čuvanja.');
                    }
                }
            } catch (error) {
                console.error('====== KRITIČNA GREŠKA PRI OBRADI FORME ======');
                console.error('Detalji greške:', error);
                console.error('Stack trace:', error.stack);
                
                // Prikaži grešku korisniku
                alert('Došlo je do greške pri čuvanju podataka: ' + error.message + '\nProverite konzolu za više detalja.');
            }
            
            console.log('====== ZAVRŠENA OBRADA KLIKA NA DUGME ======');
            return false; // Sprečavamo podrazumevanu akciju
        });
        
        // Direktno postavljanje event handlera i na nativni HTML element
        console.log('Postavljanje nativnog event listenera...');
        try {
            if ($buttonToUse && $buttonToUse[0]) {
                $buttonToUse[0].addEventListener('click', function(e) {
                    console.log('Nativni event listener za klik je aktiviran!');
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('NATIVNI KLIK NA DUGME AKTIVIRAN!!');
                    // Pokušaj direktno poslati formu nakon kraćeg intervala
                    setTimeout(function() {
                        console.log('Pokušaj slanja forme iz nativnog listenera');
                        try {
                            $form[0].submit();
                        } catch(err) {
                            console.error('Greška pri nativnom pokušaju slanja:', err);
                            alert('Neuspeo pokušaj slanja forme: ' + err.message);
                        }
                    }, 100);
                    return false;
                });
                console.log('Uspešno postavljen nativni event listener na dugme');
            } else {
                console.error('Ne mogu postaviti nativni listener - dugme nema DOM element');
            }
        } catch (e) {
            console.error('Greška pri postavljanju nativnog event listenera:', e);
        }
        
        // Postavljanje globalnog event listenera na sve submit dugmad
        console.log('Postavljanje globalnog event listenera na SVA submit dugmad...');
        $(document).on('click', 'button[type="submit"]', function(e) {
            console.log('Globalni event listener za submit dugme je aktiviran!', e.target);
        });
        
        // Postavljanje event listenera na formam
        console.log('Postavljanje event listenera na sve forme...');
        $(document).on('submit', 'form', function(e) {
            console.log('Form submit event je aktiviran!', e.target);
        });
        
        // Validacija forme
        function validateForm($form) {
            console.log('Započinjem validaciju forme...');
            const requiredFields = $form.find('[required]');
            console.log('Broj obaveznih polja:', requiredFields.length);
            
            let valid = true;
            const invalidFields = [];
            
            // Validacija obaveznih polja
            requiredFields.each(function() {
                const $field = $(this);
                const fieldId = $field.attr('id') || 'unknown';
                const fieldName = $('label[for="' + fieldId + '"]').text().trim() || fieldId;
                const fieldValue = $field.val();
                
                console.log('Validacija polja:', fieldName, 'ID:', fieldId, 'Vrednost:', fieldValue);
                
                if (!fieldValue) {
                    $field.addClass('is-invalid');
                    invalidFields.push(fieldName);
                    valid = false;
                    console.warn('Obavezno polje nije popunjeno:', fieldName, 'ID:', fieldId);
                    
                    // Skroluj do prvog polja sa greškom ako ovo jeste prvo
                    if (invalidFields.length === 1) {
                        // Odredi tab u kom se polje nalazi
                        const $tab = $field.closest('.tab-pane');
                        if ($tab.length > 0) {
                            const tabId = $tab.attr('id');
                            console.log('Polje je u tabu:', tabId);
                            // Aktiviraj tab
                            $('#companyFormTabs a[href="#' + tabId + '"]').tab('show');
                            // Skroluj do polja
                            setTimeout(() => {
                                console.log('Skrolujem do polja:', fieldId);
                                $('html, body').animate({
                                    scrollTop: $field.offset().top - 100
                                }, 500);
                                $field.focus();
                            }, 300);
                        }
                    }
                } else {
                    $field.removeClass('is-invalid');
                    console.log('Polje je validno:', fieldName);
                }
            });
            
            console.log('Rezultat validacije:', valid ? 'VALIDNA' : 'NIJE VALIDNA');
            console.log('Nevalidna polja:', invalidFields);
            
            return valid;
        }
        
        // Prikazivanje indikatora napretka na dugmetu
        function showSubmitProgress($button) {
            console.log('Prikazujem indikator napretka na dugmetu...');
            const originalText = $button.html();
            $button.data('original-text', originalText);
            console.log('Originalni tekst dugmeta:', originalText);
            
            $button.html('<i class="fas fa-spinner fa-spin"></i> Čuvam podatke...');
            $button.prop('disabled', true);
            console.log('Dugme je sada onemogućeno sa indikatorom učitavanja');
            
            // Vrati dugme u prvobitno stanje nakon određenog vremena ako se submit ne završi
            setTimeout(() => {
                if ($button.prop('disabled')) {
                    console.log('Vraćam dugme u prvobitno stanje (timeout)...');
                    $button.html($button.data('original-text'));
                    $button.prop('disabled', false);
                }
            }, 10000); // 10 sekundi timeout
        }
        
        console.log('====== COMPANY FORM SUBMIT INIT ZAVRŠEN ======');
    });
    
})(jQuery);
