/**
 * JavaScript za upravljanje IAF/EAC kodovima kompanije
 * Datoteka: company-iaf-eac.js
 */

(function($) {
    'use strict';
    
    // Globalna lista IAF/EAC kodova za trenutnu kompaniju
    let iafEacCodesData = [];
    
    // Inicijalizacija pri učitavanju skripte
    $(document).ready(function() {
        console.log('IAF/EAC kodovi: Inicijalizacija...');
        
        // Dohvati ID kompanije iz tabele
        const companyId = $('#iaf-eac-codes-list').data('company-id');
        console.log('IAF/EAC kodovi: ID kompanije:', companyId);
        
        // Ako je kompanija već kreirana (edit mode), učitaj postojeće IAF/EAC kodove
        if (companyId && companyId > 0) {
            loadIafEacCodes(companyId);
        } else {
            // Ako je nova kompanija, samo prikaži poruku da nema kodova
            updateIAFEACTable();
        }
        
        // Event handler za dodavanje novog IAF/EAC koda
        $('#addIafEacButton').on('click', function() {
            addIafEacCode();
        });
        
        // Pripremi podatke o IAF/EAC kodovima pre slanja forme
        $('form').on('submit', function() {
            prepareIafEacCodesData();
        });
        
        // Dodatno osiguraj da se prepareIafEacCodesData pozove i kad se klikne na dugme za čuvanje
        $('#saveCompanyButton').on('click', function() {
            prepareIafEacCodesData();
        });
    });
    
    /**
     * Učitava postojeće IAF/EAC kodove za kompaniju
     */
    function loadIafEacCodes(companyId) {
        console.log('IAF/EAC kodovi: Učitavanje kodova za kompaniju ID:', companyId);
        
        // Prikaži indikator učitavanja
        $('#iaf-eac-codes-list').html('<tr><td colspan="5" class="text-center"><i class="fas fa-spinner fa-spin"></i> Učitavanje kodova...</td></tr>');
        
        // Formiranje URL-a za dohvatanje IAF/EAC kodova
        // ALTERNATIVNA 1: Direktan pristup JSON podacima iz DOM-a
        const iafEacCodesInput = $('#iaf_eac_codes_data');
        if (iafEacCodesInput && iafEacCodesInput.val() && iafEacCodesInput.val() !== '[]') {
            try {
                console.log('IAF/EAC kodovi: Dohvatanje iz skrivenog polja:', iafEacCodesInput.val());
                iafEacCodesData = JSON.parse(iafEacCodesInput.val());
                updateIAFEACTable();
                return;
            } catch (e) {
                console.error('IAF/EAC kodovi: Greška pri parsiranju JSON-a iz skrivenog polja:', e);
            }
        }
        
        // ALTERNATIVA 2: Učitavanje kodova sa globalne varijable window.companyData ako postoji
        if (window.companyData && window.companyData.iafEacCodes) {
            console.log('IAF/EAC kodovi: Dohvatanje iz window.companyData');
            iafEacCodesData = window.companyData.iafEacCodes;
            updateIAFEACTable();
            return;
        }
        
        // ALTERNATIVA 3: AJAX poziv na backend
        console.log('IAF/EAC kodovi: Slanje AJAX zahteva za dohvatanje kodova');
        
        // Formiranje URL-a za dohvatanje IAF/EAC kodova - koristimo ispravnu putanju
        let apiUrl = '/company/companies/' + companyId + '/iaf-eac/list/';
        
        // Pošalji AJAX zahtev za dohvatanje IAF/EAC kodova
        $.ajax({
            url: apiUrl,
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                console.log('IAF/EAC kodovi: Uspešno učitani kodovi (AJAX):', response);
                
                // Sačuvaj kodove u globalnu varijablu
                if (response && response.codes) {
                    iafEacCodesData = response.codes;
                } else if (Array.isArray(response)) {
                    iafEacCodesData = response;
                } else {
                    console.warn('IAF/EAC kodovi: Neočekivan format odgovora:', response);
                    iafEacCodesData = [];
                }
                
                // Ažuriraj prikaz tabele
                updateIAFEACTable();
            },
            error: function(xhr, status, error) {
                console.error('IAF/EAC kodovi: Greška pri učitavanju kodova:', error);
                console.error('IAF/EAC kodovi: Status kod:', xhr.status);
                console.error('IAF/EAC kodovi: Odgovor:', xhr.responseText);
                
                // Pokušaj učitati podatke sa dodatne strane
                fallbackLoadIafEacCodes(companyId);
            }
        });
    }
    
    /**
     * Rezervni metod za učitavanje IAF/EAC kodova
     */
    function fallbackLoadIafEacCodes(companyId) {
        console.log('IAF/EAC kodovi: Pokušaj rezervnog učitavanja kodova');
        
        // Pokušaj dohvatiti IAF/EAC kodove sa stranice za detalje kompanije
        $.ajax({
            url: '/company/companies/' + companyId + '/',
            type: 'GET',
            success: function(response) {
                console.log('IAF/EAC kodovi: Uspešno dohvaćena stranica sa detaljima');
                
                // Privremeno parsiranje HTML odgovora da bismo dobili IAF/EAC kodove
                const tempDiv = $('<div>').html(response);
                const codeItems = tempDiv.find('.iaf-eac-code-item').map(function() {
                    return {
                        id: $(this).data('code-id'),
                        iaf_code: $(this).data('code'),
                        description: $(this).data('description'),
                        is_primary: $(this).data('primary') === true,
                        notes: $(this).data('notes') || ''
                    };
                }).get();
                
                if (codeItems.length > 0) {
                    console.log('IAF/EAC kodovi: Pronađeno ' + codeItems.length + ' kodova na stranici za detalje');
                    iafEacCodesData = codeItems;
                } else {
                    console.warn('IAF/EAC kodovi: Nisu pronađeni kodovi na stranici za detalje');
                    // Ako imamo postojeće podatke u skrivenom polju, pokušajmo ih učitati
                    const hiddenData = $('#iaf_eac_codes_data').val();
                    if (hiddenData && hiddenData !== '[]') {
                        try {
                            iafEacCodesData = JSON.parse(hiddenData);
                            console.log('IAF/EAC kodovi: Učitani kodovi iz skrivenog polja');
                        } catch (e) {
                            console.error('IAF/EAC kodovi: Greška pri parsiranju JSON-a iz skrivenog polja:', e);
                            iafEacCodesData = [];
                        }
                    } else {
                        iafEacCodesData = [];
                    }
                }
                
                // Ažuriraj prikaz tabele
                updateIAFEACTable();
            },
            error: function() {
                console.error('IAF/EAC kodovi: Greška pri dohvatanju stranice sa detaljima');
                // Postavi praznu listu i prikaži poruku o grešci
                iafEacCodesData = [];
                $('#iaf-eac-codes-list').html('<tr><td colspan="5" class="text-center text-danger"><i class="fas fa-exclamation-triangle"></i> Greška pri učitavanju IAF/EAC kodova.</td></tr>');
            }
        });
    }
    
    /**
     * Ažuriraj prikaz tabele sa IAF/EAC kodovima
     */
    function updateIAFEACTable() {
        console.log('IAF/EAC kodovi: Ažuriranje prikaza tabele, broj kodova:', iafEacCodesData ? iafEacCodesData.length : 0);
        console.log('IAF/EAC kodovi:', iafEacCodesData);
        
        const $tableBody = $('#iaf-eac-codes-list');
        const $noCodesMessage = $('#no-iaf-codes-message');
        
        // Proveri da li elementi postoje u DOM-u
        if ($tableBody.length === 0) {
            console.error('IAF/EAC kodovi: Nije pronađen element za prikaz tabele (#iaf-eac-codes-list)');
        }
        
        if ($noCodesMessage.length === 0) {
            console.error('IAF/EAC kodovi: Nije pronađen element za poruku o nepostojanju kodova (#no-iaf-codes-message)');
        }
        
        // Ako nema kodova, prikaži odgovarajuću poruku
        if (!iafEacCodesData || iafEacCodesData.length === 0) {
            $tableBody.html('');
            $noCodesMessage.show();
            console.log('IAF/EAC kodovi: Nema kodova, prikazujem poruku');
            return;
        }
        
        // Sakrij poruku o nepostojanju kodova
        $noCodesMessage.hide();
        console.log('IAF/EAC kodovi: Postoje kodovi, sakrivam poruku');
        
        // Generiši HTML za tabelu
        let html = '';
        for (let i = 0; i < iafEacCodesData.length; i++) {
            const code = iafEacCodesData[i];
            
            // Osiguraj da su svi podaci dostupni i pravilno formatirani
            const codeId = code.id || ('new-' + i);
            const codeText = code.iaf_code || code.code || 'N/A';
            const description = code.description || 'Bez opisa';
            const isPrimaryFlag = code.is_primary || code.primary || false;
            const notes = code.notes || '-';
            
            const isPrimary = isPrimaryFlag ? 
                '<span class="badge badge-primary">Primarni</span>' : 
                '<span class="badge badge-secondary">Sekundarni</span>';
            
            html += `
                <tr id="iaf-eac-code-${codeId}" class="iaf-eac-table-row">
                    <td><strong>${codeText}</strong></td>
                    <td>${description}</td>
                    <td>${isPrimary}</td>
                    <td>${notes}</td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button type="button" class="btn btn-outline-danger btn-remove-iaf-eac" data-index="${i}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }
        
        // Postavi HTML u tabelu
        $tableBody.html(html);
        console.log('IAF/EAC kodovi: Tabela ažurirana sa', iafEacCodesData.length, 'kodova');
        
        // Dodaj event listenere za brisanje kodova
        $('.btn-remove-iaf-eac').off('click').on('click', function() {
            const index = $(this).data('index');
            removeIafEacCode(index);
        });
        
        // Osiguraj da je tab vidljiv da bi korisnik video kodove
        if (iafEacCodesData.length > 0 && $('#iaf-tab').length > 0) {
            // Proveri da li je tab vidljiv, ako nije, dodaj vizuelni indikator
            if (!$('#iaf-tab').hasClass('active')) {
                $('#iaf-tab').append(' <span class="badge badge-info">' + iafEacCodesData.length + '</span>');
            }
        }
    }
    
    /**
     * Dodaje novi IAF/EAC kod u listu
     */
    function addIafEacCode() {
        const $select = $('#iaf_eac_code_select');
        const codeId = $select.val();
        
        if (!codeId) {
            alert('Molimo izaberite IAF/EAC kod');
            return;
        }
        
        // Proveri da li kod već postoji u listi
        for (let i = 0; i < iafEacCodesData.length; i++) {
            if (iafEacCodesData[i].id == codeId) {
                alert('Ovaj IAF/EAC kod je već dodat!');
                return;
            }
        }
        
        // Dohvati podatke o kodu
        const codeText = $select.find('option:selected').text();
        const description = $select.find('option:selected').data('description') || '';
        const notes = $('#iaf_eac_code_notes').val() || '';
        const isPrimary = $('#iaf_eac_is_primary').is(':checked');
        
        // Dohvati ID kompanije
        const companyId = $('#iaf-eac-codes-list').data('company-id');
        
        if (companyId && companyId > 0) {
            // Ako imamo ID kompanije, pošalji AJAX zahtev za dodavanje koda
            console.log('IAF/EAC kodovi: Pošiljanje AJAX zahteva za dodavanje koda');
            
            // Dohvati CSRF token
            const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
            
            // Prikaži indikator učitavanja
            const $btn = $('#addIafEacButton');
            const originalBtnHtml = $btn.html();
            $btn.html('<i class="fas fa-spinner fa-spin"></i> Dodajem...').prop('disabled', true);
            
            // Pošalji zahtev za dodavanje koda
            $.ajax({
                url: '/company/companies/' + companyId + '/iaf-eac/add/',
                type: 'POST',
                data: {
                    'iaf_eac_code_id': codeId,
                    'notes': notes,
                    'is_primary': isPrimary ? 'true' : 'false',
                    'csrfmiddlewaretoken': csrfToken
                },
                success: function(response) {
                    console.log('IAF/EAC kodovi: Uspešno dodat kod:', response);
                    
                    // Vrati dugme u prvobitno stanje
                    $btn.html(originalBtnHtml).prop('disabled', false);
                    
                    if (response.success) {
                        // Osvežei podatke
                        loadIafEacCodes(companyId);
                        
                        // Resetuj polja forme
                        $select.val('');
                        $('#iaf_eac_code_notes').val('');
                        $('#iaf_eac_is_primary').prop('checked', false);
                        
                        // Prikaži poruku o uspehu
                        if (typeof toastr !== 'undefined') {
                            toastr.success('IAF/EAC kod je uspešno dodat.');
                        } else {
                            alert('IAF/EAC kod je uspešno dodat.');
                        }
                    } else {
                        // Prikaži poruku o grešci
                        if (typeof toastr !== 'undefined') {
                            toastr.error(response.message || 'Došlo je do greške pri dodavanju IAF/EAC koda.');
                        } else {
                            alert(response.message || 'Došlo je do greške pri dodavanju IAF/EAC koda.');
                        }
                    }
                },
                error: function(xhr, status, error) {
                    console.error('IAF/EAC kodovi: Greška pri dodavanju koda:', error);
                    
                    // Vrati dugme u prvobitno stanje
                    $btn.html(originalBtnHtml).prop('disabled', false);
                    
                    // Prikaži poruku o grešci
                    if (typeof toastr !== 'undefined') {
                        toastr.error('Došlo je do greške pri dodavanju IAF/EAC koda.');
                    } else {
                        alert('Došlo je do greške pri dodavanju IAF/EAC koda.');
                    }
                }
            });
        } else {
            // Ako nemamo ID kompanije (nova kompanija), samo dodaj kod u lokalnu listu
            // Ako je korisnik označio novi kod kao primarni, označi sve ostale kao sekundarne
            if (isPrimary) {
                for (let i = 0; i < iafEacCodesData.length; i++) {
                    iafEacCodesData[i].is_primary = false;
                }
            }
            
            // Dodaj novi kod u listu
            iafEacCodesData.push({
                id: parseInt(codeId),
                iaf_code: codeText.split(' - ')[0], // Izdvoji samo kod iz teksta
                description: description,
                is_primary: isPrimary,
                notes: notes
            });
            
            // Ažuriraj prikaz tabele
            updateIAFEACTable();
            
            // Resetuj polja forme
            $select.val('');
            $('#iaf_eac_code_notes').val('');
            $('#iaf_eac_is_primary').prop('checked', false);
        }
    }
    
    /**
     * Uklanja IAF/EAC kod iz liste
     */
    function removeIafEacCode(index) {
        if (confirm('Da li ste sigurni da želite da uklonite ovaj IAF/EAC kod?')) {
            // Dohvati ID kompanije i kod koji se briše
            const companyId = $('#iaf-eac-codes-list').data('company-id');
            const code = iafEacCodesData[index];
            
            if (companyId && companyId > 0 && code && code.id) {
                // Ako je kompanija već kreirana i kod ima ID u bazi, briši preko AJAX-a
                console.log('IAF/EAC kodovi: Brisanje koda preko AJAX-a, ID:', code.id);
                
                // Dohvati CSRF token
                const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
                
                // Pošalji AJAX zahtev za brisanje koda
                $.ajax({
                    url: '/company/companies/' + companyId + '/iaf-eac/' + code.id + '/delete/',
                    type: 'POST',
                    data: {
                        'csrfmiddlewaretoken': csrfToken
                    },
                    success: function(response) {
                        console.log('IAF/EAC kodovi: Uspešno obrisan kod:', response);
                        
                        if (response.success) {
                            // Ukloni kod iz lokalne liste
                            iafEacCodesData.splice(index, 1);
                            updateIAFEACTable();
                            
                            // Prikaži poruku o uspehu
                            if (typeof toastr !== 'undefined') {
                                toastr.success('IAF/EAC kod je uspešno obrisan.');
                            }
                        } else {
                            // Prikaži poruku o grešci
                            if (typeof toastr !== 'undefined') {
                                toastr.error(response.message || 'Došlo je do greške pri brisanju IAF/EAC koda.');
                            } else {
                                alert(response.message || 'Došlo je do greške pri brisanju IAF/EAC koda.');
                            }
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('IAF/EAC kodovi: Greška pri brisanju koda:', error);
                        
                        // Prikaži poruku o grešci
                        if (typeof toastr !== 'undefined') {
                            toastr.error('Došlo je do greške pri brisanju IAF/EAC koda.');
                        } else {
                            alert('Došlo je do greške pri brisanju IAF/EAC koda.');
                        }
                    }
                });
            } else {
                // Ako je nova kompanija ili kod nema ID, samo ukloni iz lokalne liste
                iafEacCodesData.splice(index, 1);
                updateIAFEACTable();
            }
        }
    }
    
    /**
     * Priprema podatke o IAF/EAC kodovima za slanje forme
     */
    function prepareIafEacCodesData() {
        $('#iaf_eac_codes_data').val(JSON.stringify(iafEacCodesData));
    }
    
    // Izloži funkcije globalnom opsegu za potrebe debug-a
    window.iafEacModule = {
        loadIafEacCodes: loadIafEacCodes,
        updateIAFEACTable: updateIAFEACTable,
        addIafEacCode: addIafEacCode
    };
    
})(jQuery);
