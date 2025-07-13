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
        console.log('IAF/EAC kodovi: Elementi u DOM-u:', {
            'iaf-eac-codes-list': $('#iaf-eac-codes-list').length,
            'no-iaf-codes-message': $('#no-iaf-codes-message').length,
            'addIafEacButton': $('#addIafEacButton').length,
            'iaf_eac_codes_data': $('#iaf_eac_codes_data').length,
            'iaf_eac_code': $('#iaf_eac_code').length
        });
        
        // Ako je kompanija već kreirana (edit mode), učitaj postojeće IAF/EAC kodove
        if (companyId && companyId > 0) {
            console.log('IAF/EAC kodovi: Učitavanje postojećih kodova za kompaniju ID:', companyId);
            loadIafEacCodes(companyId);
        } else {
            // Ako je nova kompanija, samo prikaži poruku da nema kodova
            console.log('IAF/EAC kodovi: Nova kompanija, nema kodova za učitavanje');
            updateIAFEACTable();
        }
        
        // Event handler za dodavanje novog IAF/EAC koda
        $('#addIafEacButton').on('click', function() {
            console.log('IAF/EAC kodovi: Kliknuto dugme za dodavanje koda');
            addIafEacCode();
        });
        
        // Pripremi podatke o IAF/EAC kodovima pre slanja forme
        $('form').on('submit', function() {
            console.log('IAF/EAC kodovi: Priprema podataka pre slanja forme');
            prepareIafEacCodesData();
        });
        
        // Dodatno osiguraj da se prepareIafEacCodesData pozove i kad se klikne na dugme za čuvanje
        $('#saveCompanyButton').on('click', function() {
            console.log('IAF/EAC kodovi: Priprema podataka pre klika na dugme za čuvanje');
            prepareIafEacCodesData();
        });
        
        // Dodatno - proveri da li postoje globalni podaci o IAF/EAC kodovima
        if (window.companyData && window.companyData.iafEacCodes) {
            console.log('IAF/EAC kodovi: Pronađeni globalni podaci o kodovima:', window.companyData.iafEacCodes);
        }
    });
    
    /**
     * Učitava postojeće IAF/EAC kodove za kompaniju
     */
    function loadIafEacCodes(companyId) {
        console.log('IAF/EAC kodovi: Učitavanje kodova za kompaniju ID:', companyId);
        
        // Prikaži indikator učitavanja
        $('#iaf-eac-codes-list').html('<tr><td colspan="3" class="text-center"><i class="fas fa-spinner fa-spin"></i> Učitavanje kodova...</td></tr>');
        
        // KORAK 1: Proveri da li već imamo podatke u skrivenom polju
        const iafEacCodesInput = $('#iaf_eac_codes_data');
        if (iafEacCodesInput && iafEacCodesInput.val()) {
            try {
                // Proveri da li je vrednost HTML umesto JSON-a
                const value = iafEacCodesInput.val();
                if (value.trim().startsWith('<!DOCTYPE html>') || value.trim().startsWith('<html')) {
                    console.warn('IAF/EAC kodovi: Skriveno polje sadrži HTML umesto JSON-a. Moguće da korisnik nije prijavljen.');
                    
                    // Proveri da li je to stranica za prijavu koristeći globalnu funkciju
                    if (window.sessionHandler && window.sessionHandler.isLoginPage(value)) {
                        console.log('IAF/EAC kodovi: Detektovana stranica za prijavu, korisnik nije prijavljen');
                        if (window.sessionHandler.handleSessionExpired) {
                            window.sessionHandler.handleSessionExpired();
                        }
                        return;
                    }
                } else if (value !== '[]' && value.trim() !== '') {
                    // Pokušaj parsirati JSON
                    console.log('IAF/EAC kodovi: Dohvatanje iz skrivenog polja:', value);
                    iafEacCodesData = JSON.parse(value);
                    console.log('IAF/EAC kodovi: Uspešno učitani kodovi iz skrivenog polja:', iafEacCodesData);
                    updateIAFEACTable();
                    return;
                }
            } catch (e) {
                console.error('IAF/EAC kodovi: Greška pri parsiranju JSON-a iz skrivenog polja:', e);
            }
        } else {
            console.log('IAF/EAC kodovi: Nema podataka u skrivenom polju ili je prazno');
        }
        
        // KORAK 2: Proveri da li postoje podaci u window.companyData
        if (window.companyData && window.companyData.iafEacCodes) {
            console.log('IAF/EAC kodovi: Dohvatanje iz window.companyData');
            iafEacCodesData = window.companyData.iafEacCodes;
            console.log('IAF/EAC kodovi: Uspešno učitani kodovi iz window.companyData:', iafEacCodesData);
            updateIAFEACTable();
            return;
        } else {
            console.log('IAF/EAC kodovi: Nema podataka u window.companyData ili ne postoji');
        }
        
        // KORAK 3: Direktno dohvatanje kodova preko API-ja
        console.log('IAF/EAC kodovi: Direktno dohvatanje preko API-ja');
        
        // Probaj prvo sa standardnom putanjom
        tryLoadFromAPI(companyId, '/companies/' + companyId + '/iaf-eac/list/');
    }
    
    /**
     * Pokušava učitati IAF/EAC kodove preko API-ja sa različitim putanjama
     */
    function tryLoadFromAPI(companyId, apiUrl) {
        console.log('IAF/EAC kodovi: Pokušaj učitavanja sa URL-a:', apiUrl);
        
        // Pošalji AJAX zahtev za dohvatanje IAF/EAC kodova
        $.ajax({
            url: apiUrl,
            type: 'GET',
            dataType: 'json',
            beforeSend: function(xhr) {
                // Proveri da li postoji CSRF token, što je indikator da je korisnik prijavljen
                if (!$('input[name="csrfmiddlewaretoken"]').val()) {
                    console.warn('IAF/EAC kodovi: Korisnik možda nije prijavljen, CSRF token nije pronađen');
                }
            },
            success: function(response) {
                // Proveri da li je odgovor HTML umesto JSON-a (može se desiti ako je jQuery parsirao HTML kao objekat)
                if (typeof response === 'string' && (response.includes('<!DOCTYPE html>') || response.includes('<html'))) {
                    console.warn('IAF/EAC kodovi: Server je vratio HTML umesto JSON-a. Moguće da korisnik nije prijavljen.');
                    
                    // Proveri da li je to stranica za prijavu koristeći globalnu funkciju
                    if (window.sessionHandler && window.sessionHandler.isLoginPage(response)) {
                        console.log('IAF/EAC kodovi: Detektovana stranica za prijavu, korisnik nije prijavljen');
                        if (window.sessionHandler.handleSessionExpired) {
                            window.sessionHandler.handleSessionExpired();
                        } else {
                            // Rezervni mehanizam ako globalna funkcija nije dostupna
                            console.error('IAF/EAC kodovi: Sesija je istekla, ali funkcija za rukovanje nije dostupna');
                            fallbackLoadIafEacCodes(companyId);
                        }
                        return;
                    }
                }
                
                // Proveri da li je odgovor objekat koji sadrži HTML (jQuery može parsirati HTML kao objekat)
                if (response && typeof response === 'object' && response.documentElement) {
                    console.warn('IAF/EAC kodovi: Server je vratio HTML dokument umesto JSON-a.');
                    
                    // Proveri da li je to stranica za prijavu koristeći globalnu funkciju
                    if (window.sessionHandler && window.sessionHandler.isLoginPage(response)) {
                        console.log('IAF/EAC kodovi: Detektovana stranica za prijavu, korisnik nije prijavljen');
                        if (window.sessionHandler.handleSessionExpired) {
                            window.sessionHandler.handleSessionExpired();
                        } else {
                            // Rezervni mehanizam ako globalna funkcija nije dostupna
                            console.error('IAF/EAC kodovi: Sesija je istekla, ali funkcija za rukovanje nije dostupna');
                            fallbackLoadIafEacCodes(companyId);
                        }
                        return;
                    }
                }
                
                console.log('IAF/EAC kodovi: Uspešno učitani kodovi (AJAX):', response);
                
                // Sačuvaj kodove u globalnu varijablu
                if (response && response.codes) {
                    // Format odgovora: { success: true, codes: [...] }
                    iafEacCodesData = response.codes;
                    console.log('IAF/EAC kodovi: Kodovi učitani iz response.codes, broj kodova:', iafEacCodesData.length);
                } else if (response && response.success === true && Array.isArray(response.codes)) {
                    // Format odgovora: { success: true, codes: [...] }
                    iafEacCodesData = response.codes;
                    console.log('IAF/EAC kodovi: Kodovi učitani iz response.codes, broj kodova:', iafEacCodesData.length);
                } else if (Array.isArray(response)) {
                    // Format odgovora: [...]
                    iafEacCodesData = response;
                    console.log('IAF/EAC kodovi: Kodovi učitani iz niza, broj kodova:', iafEacCodesData.length);
                } else {
                    console.warn('IAF/EAC kodovi: Neočekivan format odgovora:', response);
                    iafEacCodesData = [];
                }
                
                // Ažuriraj prikaz tabele
                updateIAFEACTable();
                
                // Sačuvaj kodove u skriveno polje za buduće korišćenje
                if (iafEacCodesData.length > 0) {
                    $('#iaf_eac_codes_data').val(JSON.stringify(iafEacCodesData));
                    console.log('IAF/EAC kodovi: Kodovi sačuvani u skriveno polje');
                }
            },
            error: function(xhr, status, error) {
                console.error('IAF/EAC kodovi: Greška pri učitavanju kodova sa URL-a ' + apiUrl + ':', error);
                console.error('IAF/EAC kodovi: Status kod:', xhr.status);
                
                // Proveri da li je odgovor HTML stranica za prijavu koristeći globalnu funkciju
                if (xhr.responseText && window.sessionHandler && window.sessionHandler.isLoginPage(xhr.responseText)) {
                    console.warn('IAF/EAC kodovi: Server je vratio stranicu za prijavu. Korisnik nije prijavljen.');
                    
                    // Koristi globalnu funkciju za rukovanje sesijom ako je dostupna
                    if (window.sessionHandler && window.sessionHandler.handleSessionExpired) {
                        console.log('IAF/EAC kodovi: Korišćenje globalne funkcije za rukovanje sesijom');
                        window.sessionHandler.handleSessionExpired();
                    } else {
                        // Rezervni mehanizam ako globalna funkcija nije dostupna
                        console.log('IAF/EAC kodovi: Korišćenje lokalnog mehanizma za rukovanje sesijom');
                        
                        // Prikaži poruku korisniku
                        if (typeof toastr !== 'undefined') {
                            toastr.warning('Sesija je istekla. Bićete preusmereni na stranicu za prijavu.', '', {
                                timeOut: 3000,
                                closeButton: true,
                                progressBar: true,
                                positionClass: 'toast-top-center'
                            });
                        } else {
                            alert('Sesija je istekla. Bićete preusmereni na stranicu za prijavu.');
                        }
                        
                        // Sačuvaj trenutnu lokaciju da bi se korisnik vratio nakon prijave
                        localStorage.setItem('redirectAfterLogin', window.location.href);
                        console.log('IAF/EAC kodovi: Sačuvana lokacija za preusmeravanje nakon prijave:', window.location.href);
                        
                        // Preusmeravanje na stranicu za prijavu nakon kratke pauze
                        console.log('IAF/EAC kodovi: Preusmeravanje na stranicu za prijavu za 3 sekunde...');
                        setTimeout(function() {
                            console.log('IAF/EAC kodovi: Preusmeravanje na stranicu za prijavu...');
                            window.location.href = '/accounts/login/';
                        }, 3000);
                    }
                    
                    // Ipak učitaj kodove rezervnim metodom dok čekamo preusmeravanje
                    console.log('IAF/EAC kodovi: Prelazak na rezervni metod učitavanja');
                    fallbackLoadIafEacCodes(companyId);
                    return;
                }
                
                // Pokušaj sa alternativnim URL-ovima ako trenutni nije uspeo
                if (apiUrl === '/companies/' + companyId + '/iaf-eac/list/') {
                    // Pokušaj sa alternativnom putanjom koja uključuje prefiks 'company'
                    console.log('IAF/EAC kodovi: Pokušaj sa alternativnom putanjom (company prefix)');
                    tryLoadFromAPI(companyId, '/company/companies/' + companyId + '/iaf-eac/list/');
                } else if (apiUrl === '/company/companies/' + companyId + '/iaf-eac/list/') {
                    // Pokušaj sa API putanjom
                    console.log('IAF/EAC kodovi: Pokušaj sa API putanjom');
                    tryLoadFromAPI(companyId, '/api/company/' + companyId + '/iaf-codes/');
                } else {

// Event handler za dodavanje novog IAF/EAC koda
$('#addIafEacButton').on('click', function() {
    console.log('IAF/EAC kodovi: Kliknuto dugme za dodavanje koda');
    addIafEacCode();
});

// Pripremi podatke o IAF/EAC kodovima pre slanja forme
$('form').on('submit', function() {
    console.log('IAF/EAC kodovi: Priprema podataka pre slanja forme');
    prepareIafEacCodesData();
});

// Dodatno osiguraj da se prepareIafEacCodesData pozove i kad se klikne na dugme za čuvanje
$('#saveCompanyButton').on('click', function() {
    console.log('IAF/EAC kodovi: Priprema podataka pre klika na dugme za čuvanje');
    prepareIafEacCodesData();
});

// Dodatno - proveri da li postoje globalni podaci o IAF/EAC kodovima
if (window.companyData && window.companyData.iafEacCodes) {
    console.log('IAF/EAC kodovi: Pronađeni globalni podaci o kodovima:', window.companyData.iafEacCodes);
}

/**
 * Učitava postojeće IAF/EAC kodove za kompaniju
 */
function loadIafEacCodes(companyId) {
    console.log('IAF/EAC kodovi: Učitavanje kodova za kompaniju ID:', companyId);

    // Prikaži indikator učitavanja
    $('#iaf-eac-codes-list').html('<tr><td colspan="3" class="text-center"><i class="fas fa-spinner fa-spin"></i> Učitavanje kodova...</td></tr>');

    // KORAK 1: Proveri da li već imamo podatke u skrivenom polju
    const iafEacCodesInput = $('#iaf_eac_codes_data');
    if (iafEacCodesInput && iafEacCodesInput.val() && iafEacCodesInput.val() !== '[]') {
        try {
            console.log('IAF/EAC kodovi: Dohvatanje iz skrivenog polja:', iafEacCodesInput.val());
            iafEacCodesData = JSON.parse(iafEacCodesInput.val());
            console.log('IAF/EAC kodovi: Uspešno učitani kodovi iz skrivenog polja:', iafEacCodesData);
            updateIAFEACTable();
            return;
        } catch (e) {
            console.error('IAF/EAC kodovi: Greška pri parsiranju JSON-a iz skrivenog polja:', e);
        }
    } else {
        console.log('IAF/EAC kodovi: Nema podataka u skrivenom polju ili je prazno');
    }

    // KORAK 2: Proveri da li postoje podaci u window.companyData
    if (window.companyData && window.companyData.iafEacCodes) {
        console.log('IAF/EAC kodovi: Dohvatanje iz window.companyData');
        iafEacCodesData = window.companyData.iafEacCodes;
        console.log('IAF/EAC kodovi: Uspešno učitani kodovi iz window.companyData:', iafEacCodesData);
        updateIAFEACTable();
        return;
    } else {
        console.log('IAF/EAC kodovi: Nema podataka u window.companyData ili ne postoji');
    }

    // KORAK 3: Direktno dohvatanje kodova preko API-ja
    console.log('IAF/EAC kodovi: Direktno dohvatanje preko API-ja');

    // Probaj prvo sa standardnom putanjom
    tryLoadFromAPI(companyId, '/companies/' + companyId + '/iaf-eac/list/');
}

/**
 * Pokušava učitati IAF/EAC kodove preko API-ja sa različitim putanjama
 */
function tryLoadFromAPI(companyId, apiUrl) {
    console.log('IAF/EAC kodovi: Pokušaj učitavanja sa URL-a:', apiUrl);

    // Pošalji AJAX zahtev za dohvatanje IAF/EAC kodova
    $.ajax({
        url: apiUrl,
        type: 'GET',
        dataType: 'json',
        beforeSend: function(xhr) {
            // Proveri da li postoji CSRF token, što je indikator da je korisnik prijavljen
            if (!$('input[name="csrfmiddlewaretoken"]').val()) {
                console.warn('IAF/EAC kodovi: Korisnik možda nije prijavljen, CSRF token nije pronađen');
            }
        },
        success: function(response) {
            // Proveri da li je odgovor HTML umesto JSON-a (može se desiti ako je jQuery parsirao HTML kao objekat)
            if (typeof response === 'string' && (response.includes('<!DOCTYPE html>') || response.includes('<html'))) {
                console.warn('IAF/EAC kodovi: Server je vratio HTML umesto JSON-a. Moguće da korisnik nije prijavljen.');

                // Proveri da li je to stranica za prijavu
                if (response.includes('<title>Prijava | ISOQAR</title>') || response.includes('login-page')) {
                    // Koristi globalnu funkciju za rukovanje sesijom ako je dostupna
                    if (window.sessionHandler && window.sessionHandler.handleSessionExpired) {
                        window.sessionHandler.handleSessionExpired();
                    } else {
                        // Rezervni mehanizam ako globalna funkcija nije dostupna
                        console.error('IAF/EAC kodovi: Sesija je istekla, ali funkcija za rukovanje nije dostupna');
                        
                        // Prikaži poruku korisniku
                        if (typeof toastr !== 'undefined') {
                            toastr.error('Niste prijavljeni. Bićete preusmereni na stranicu za prijavu.');
                        } else {
                            alert('Niste prijavljeni. Bićete preusmereni na stranicu za prijavu.');
                        }
                        
                        // Sačuvaj trenutnu lokaciju da bi se korisnik vratio nakon prijave
                        localStorage.setItem('redirectAfterLogin', window.location.href);
                        
                        // Preusmeravanje na stranicu za prijavu nakon kratke pauze
                        setTimeout(function() {
                            window.location.href = '/accounts/login/';
                        }, 2000);
                    }
                    return;
                }
            }
            
            // Proveri da li je odgovor objekat koji sadrži HTML (jQuery može parsirati HTML kao objekat)
            if (response && typeof response === 'object' && response.documentElement) {
                console.warn('IAF/EAC kodovi: Server je vratio HTML dokument umesto JSON-a.');
                
                // Proveri da li je to stranica za prijavu koristeći globalnu funkciju
                if (window.sessionHandler && window.sessionHandler.isLoginPage(response)) {
                    console.log('IAF/EAC kodovi: Detektovana stranica za prijavu, korisnik nije prijavljen');
                    if (window.sessionHandler.handleSessionExpired) {
                        window.sessionHandler.handleSessionExpired();
                    } else {
                        // Rezervni mehanizam ako globalna funkcija nije dostupna
                        console.error('IAF/EAC kodovi: Sesija je istekla, ali funkcija za rukovanje nije dostupna');
                        fallbackLoadIafEacCodes(companyId);
                    }
                    return;
                }
            }
            
            console.log('IAF/EAC kodovi: Uspešno učitani kodovi (AJAX):', response);
            
            // Sačuvaj kodove u globalnu varijablu
            if (response && response.codes) {
                // Format odgovora: { success: true, codes: [...] }
                iafEacCodesData = response.codes;
                console.log('IAF/EAC kodovi: Kodovi učitani iz response.codes, broj kodova:', iafEacCodesData.length);
            } else if (response && response.success === true && Array.isArray(response.codes)) {
                // Format odgovora: { success: true, codes: [...] }
                iafEacCodesData = response.codes;
                console.log('IAF/EAC kodovi: Kodovi učitani iz response.codes, broj kodova:', iafEacCodesData.length);
            } else if (Array.isArray(response)) {
                // Format odgovora: [...]
                iafEacCodesData = response;
                console.log('IAF/EAC kodovi: Kodovi učitani iz niza, broj kodova:', iafEacCodesData.length);
            } else {
                console.warn('IAF/EAC kodovi: Neočekivan format odgovora:', response);
                iafEacCodesData = [];
            }
            
            // Ažuriraj prikaz tabele
            updateIAFEACTable();
            
            // Sačuvaj kodove u skriveno polje za buduće korišćenje
            if (iafEacCodesData.length > 0) {
                $('#iaf_eac_codes_data').val(JSON.stringify(iafEacCodesData));
                console.log('IAF/EAC kodovi: Kodovi sačuvani u skriveno polje');
            }
        },
        error: function(xhr, status, error) {
            console.error('IAF/EAC kodovi: Greška pri učitavanju kodova sa URL-a ' + apiUrl + ':', error);
            console.error('IAF/EAC kodovi: Status kod:', xhr.status);
            
            // Proveri da li je odgovor HTML stranica za prijavu koristeći globalnu funkciju
            if (xhr.responseText && window.sessionHandler && window.sessionHandler.isLoginPage(xhr.responseText)) {
                console.warn('IAF/EAC kodovi: Server je vratio stranicu za prijavu. Korisnik nije prijavljen.');
                
                // Koristi globalnu funkciju za rukovanje sesijom ako je dostupna
                if (window.sessionHandler && window.sessionHandler.handleSessionExpired) {
                    console.log('IAF/EAC kodovi: Korišćenje globalne funkcije za rukovanje sesijom');
                    window.sessionHandler.handleSessionExpired();
                } else {
                    // Rezervni mehanizam ako globalna funkcija nije dostupna
                    console.log('IAF/EAC kodovi: Korišćenje lokalnog mehanizma za rukovanje sesijom');
                    
                    // Prikaži poruku korisniku
                    if (typeof toastr !== 'undefined') {
                        toastr.warning('Sesija je istekla. Bićete preusmereni na stranicu za prijavu.', '', {
                            timeOut: 3000,
                            closeButton: true,
                            progressBar: true,
                            positionClass: 'toast-top-center'
                        });
                    } else {
                        alert('Sesija je istekla. Bićete preusmereni na stranicu za prijavu.');
                    }
                    
                    // Sačuvaj trenutnu lokaciju da bi se korisnik vratio nakon prijave
                    localStorage.setItem('redirectAfterLogin', window.location.href);
                    console.log('IAF/EAC kodovi: Sačuvana lokacija za preusmeravanje nakon prijave:', window.location.href);
                    
                    // Preusmeravanje na stranicu za prijavu nakon kratke pauze
                    console.log('IAF/EAC kodovi: Preusmeravanje na stranicu za prijavu za 3 sekunde...');
                    setTimeout(function() {
                        console.log('IAF/EAC kodovi: Preusmeravanje na stranicu za prijavu...');
                        window.location.href = '/accounts/login/';
                    }, 3000);
                }
                
                // Ipak učitaj kodove rezervnim metodom dok čekamo preusmeravanje
                console.log('IAF/EAC kodovi: Prelazak na rezervni metod učitavanja');
                fallbackLoadIafEacCodes(companyId);
                return;
            }
            
            // Pokušaj sa alternativnim URL-ovima ako trenutni nije uspeo
            if (apiUrl === '/companies/' + companyId + '/iaf-eac/list/') {
                // Pokušaj sa alternativnom putanjom koja uključuje prefiks 'company'
                console.log('IAF/EAC kodovi: Pokušaj sa alternativnom putanjom (company prefix)');
                tryLoadFromAPI(companyId, '/company/companies/' + companyId + '/iaf-eac/list/');
            } else if (apiUrl === '/company/companies/' + companyId + '/iaf-eac/list/') {
                // Pokušaj sa API putanjom
                console.log('IAF/EAC kodovi: Pokušaj sa API putanjom');
                tryLoadFromAPI(companyId, '/api/company/' + companyId + '/iaf-codes/');
            } else {
                // Ako su sve putanje isprobane i nijedna nije uspela, pokušaj sa rezervnim metodom
                console.log('IAF/EAC kodovi: Sve API putanje isprobane bez uspeha, pokušaj rezervnog metoda');
                fallbackLoadIafEacCodes(companyId);
            }
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
                updateIAFEACTable();
            }
        });
    }
    
    /**
                    <td>
                        ${isPrimary}
                        <button type="button" class="btn btn-sm btn-outline-danger float-right btn-remove-iaf-eac" data-index="${i}">
                            <i class="fas fa-trash"></i>
                        </button>
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
        console.log('IAF/EAC kodovi: Dodavanje novog koda');
        
        // Dohvati vrednosti iz forme
        const $select = $('#iaf_eac_code');
        const codeId = $select.val();
        const codeText = $select.find('option:selected').text();
        const notes = $('#iaf_eac_code_notes').val();
        const isPrimary = $('#iaf_eac_is_primary').is(':checked');
        
        console.log('IAF/EAC kodovi: Podaci za dodavanje:', {
            codeId: codeId,
            codeText: codeText,
            notes: notes,
            isPrimary: isPrimary
        });
        
        // Validacija
        if (!codeId) {
            console.error('IAF/EAC kodovi: Nije izabran kod');
            if (typeof toastr !== 'undefined') {
                toastr.error('Molimo izaberite IAF/EAC kod.');
            } else {
                alert('Molimo izaberite IAF/EAC kod.');
            }
            return;
        }
        
        // Proveri da li kod već postoji u listi
        const existingIndex = iafEacCodesData.findIndex(code => 
            (code.id && code.id.toString() === codeId.toString()) || 
            (code.iaf_code === codeId.toString())
        );
        
        if (existingIndex !== -1) {
            console.error('IAF/EAC kodovi: Kod već postoji u listi');
            if (typeof toastr !== 'undefined') {
                toastr.warning('Ovaj IAF/EAC kod je već dodat.');
            } else {
                alert('Ovaj IAF/EAC kod je već dodat.');
            }
            return;
        }
        
        // Dohvati ID kompanije
        const companyId = $('#iaf-eac-codes-list').data('company-id');
        console.log('IAF/EAC kodovi: Dodavanje koda za kompaniju ID:', companyId);
        
        // Ako je kompanija već kreirana, dodaj kod preko AJAX-a
        if (companyId && companyId > 0) {
            // Dohvati CSRF token
            const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
            
            // Prikaži indikator učitavanja
            const $addButton = $('#addIafEacButton');
            const originalText = $addButton.html();
            $addButton.html('<i class="fas fa-spinner fa-spin"></i> Dodajem...');
            $addButton.prop('disabled', true);
            
            // Izdvoji samo kod iz teksta (npr. "01 - Agriculture" -> "01")
            const description = codeText.includes(' - ') ? codeText.split(' - ').slice(1).join(' - ') : codeText;
            const codeValue = codeText.includes(' - ') ? codeText.split(' - ')[0] : codeText;
            
            console.log('IAF/EAC kodovi: Izdvojeni podaci:', {
                codeValue: codeValue,
                description: description
            });
            
            // Pošalji AJAX zahtev za dodavanje koda
            $.ajax({
                url: '/company/companies/' + companyId + '/iaf-eac/add/',
                type: 'POST',
                data: {
                    'csrfmiddlewaretoken': csrfToken,
                    'iaf_eac_code': codeId,
                    'is_primary': isPrimary ? 'true' : 'false',
                    'notes': notes
                },
                success: function(response) {
                    console.log('IAF/EAC kodovi: Uspešno dodat kod:', response);
                    
                    // Resetuj dugme
                    $addButton.html(originalText);
                    $addButton.prop('disabled', false);
                    
                    // Prikaži poruku o uspehu
                    if (typeof toastr !== 'undefined') {
                        toastr.success('IAF/EAC kod je uspešno dodat.');
                    }
                    
                    // Dodaj novi kod u listu (sa ID-em iz odgovora)
                    if (response && response.id) {
                        iafEacCodesData.push({
                            id: response.id,
                            iaf_code: codeValue,
                            description: description,
                            is_primary: isPrimary,
                            notes: notes
                        });
                    } else {
                        // Ako nema ID-a u odgovoru, koristi privremeni ID
                        iafEacCodesData.push({
                            id: 'new-' + new Date().getTime(),
                            iaf_code: codeValue,
                            description: description,
                            is_primary: isPrimary,
                            notes: notes
                        });
                    }
                    
                    // Ažuriraj prikaz tabele
                    updateIAFEACTable();
                    
                    // Resetuj polja forme
                    $select.val('');
                    $('#iaf_eac_code_notes').val('');
                    $('#iaf_eac_is_primary').prop('checked', false);
                },
                error: function(xhr, status, error) {
                    console.error('IAF/EAC kodovi: Greška pri dodavanju koda:', error);
                    console.error('IAF/EAC kodovi: Status kod:', xhr.status);
                    console.error('IAF/EAC kodovi: Odgovor:', xhr.responseText);
                    
                    // Resetuj dugme
                    $addButton.html(originalText);
                    $addButton.prop('disabled', false);
                    
                    // Prikaži poruku o grešci
                    if (typeof toastr !== 'undefined') {
                        toastr.error('Došlo je do greške pri dodavanju IAF/EAC koda.');
                    } else {
                        alert('Došlo je do greške pri dodavanju IAF/EAC koda.');
                    }
                }
            });
        } else {
            
            if (response.success && response.codes) {
                // Uspešno dohvaćeni kodovi
                iafEacCodesData = response.codes;
                console.log('IAF/EAC kodovi: Broj učitanih kodova:', iafEacCodesData.length);
                
                // Ažuriraj prikaz tabele
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
     * Ažurira prikaz tabele sa IAF/EAC kodovima
     */
    function updateIAFEACTable() {
        console.log('IAF/EAC kodovi: Ažuriranje prikaza tabele, broj kodova:', iafEacCodesData.length);
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
            
            const isPrimary = isPrimaryFlag ? 
                '<span class="badge badge-primary">Primarni</span>' : 
                '<span class="badge badge-secondary">Sekundarni</span>';
            
            html += `
                <tr id="iaf-eac-code-${codeId}" class="iaf-eac-table-row">
                    <td><strong>${codeText}</strong></td>
                    <td>${description}</td>
                    <td>
                        ${isPrimary}
                        <div class="btn-group float-right">
                            ${!isPrimaryFlag ? `<button type="button" class="btn btn-sm btn-info btn-set-primary-iaf-eac" data-index="${i}" title="Postavi kao primarni">
                                <i class="fas fa-star"></i>
                            </button>` : ''}
                            <button type="button" class="btn btn-sm btn-danger btn-remove-iaf-eac" data-index="${i}" title="Obriši kod">
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
        
        // Dodaj event listenere za postavljanje koda kao primarnog
        $('.btn-set-primary-iaf-eac').off('click').on('click', function() {
            const index = $(this).data('index');
            setPrimaryIafEacCode(index);
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
     * Postavlja IAF/EAC kod kao primarni
     */
    function setPrimaryIafEacCode(index) {
        console.log('IAF/EAC kodovi: Postavljanje koda kao primarnog, index:', index);
        
        if (index < 0 || index >= iafEacCodesData.length) {
            console.error('IAF/EAC kodovi: Nevažeći index za postavljanje primarnog koda:', index);
            return;
        }
        
        const code = iafEacCodesData[index];
        const companyId = $('#iaf-eac-codes-list').data('company-id');
        
        if (companyId && companyId > 0 && code.id) {
            // Dohvati CSRF token
            const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
            
            // Proveri da li je korisnik prijavljen
            if (!csrfToken) {
                console.error('IAF/EAC kodovi: CSRF token nije pronađen. Korisnik nije prijavljen.');
                
                // Prikaži poruku korisniku
                if (typeof toastr !== 'undefined') {
                    toastr.error('Niste prijavljeni. Bićete preusmereni na stranicu za prijavu.');
                } else {
                    alert('Niste prijavljeni. Bićete preusmereni na stranicu za prijavu.');
                }
                
                // Sačuvaj trenutnu lokaciju da bi se korisnik vratio nakon prijave
                localStorage.setItem('redirectAfterLogin', window.location.href);
                
                // Preusmeravanje na stranicu za prijavu nakon kratke pauze
                setTimeout(function() {
                    window.location.href = '/accounts/login/';
                }, 2000);
                
                return;
            }
            
            // Prikaži indikator učitavanja
            const $row = $('#iaf-eac-code-' + code.id);
            const $setPrimaryButton = $row.find('.btn-set-primary-iaf-eac');
            const originalHtml = $setPrimaryButton.html();
            $setPrimaryButton.html('<i class="fas fa-spinner fa-spin"></i>');
            $setPrimaryButton.prop('disabled', true);
            
            // Pošalji AJAX zahtev za postavljanje koda kao primarnog
            $.ajax({
                url: '/company/companies/' + companyId + '/iaf-eac/' + code.id + '/set-primary/',
                type: 'POST',
                data: {
                    'csrfmiddlewaretoken': csrfToken
                },
                success: function(response) {
                    console.log('IAF/EAC kodovi: Uspešno postavljen primarni kod:', response);
                    
                    if (response.success) {
                        // Ažuriraj lokalne podatke
                        iafEacCodesData.forEach(function(c) {
                            c.is_primary = false;
                        });
                        iafEacCodesData[index].is_primary = true;
                        
                        // Ažuriraj prikaz tabele
                        updateIAFEACTable();
                        
                        // Prikaži poruku o uspehu
                        if (typeof toastr !== 'undefined') {
                            toastr.success('IAF/EAC kod je uspešno postavljen kao primarni.');
                        }
                    } else {
                        // Prikaži poruku o grešci
                        if (typeof toastr !== 'undefined') {
                            toastr.error(response.message || 'Došlo je do greške pri postavljanju primarnog IAF/EAC koda.');
                        } else {
                            alert(response.message || 'Došlo je do greške pri postavljanju primarnog IAF/EAC koda.');
                        }
                        
                        // Vrati dugme u prvobitno stanje
                        $setPrimaryButton.html(originalHtml);
                        $setPrimaryButton.prop('disabled', false);
                    }
                },
                error: function(xhr, status, error) {
                    console.error('IAF/EAC kodovi: Greška pri postavljanju primarnog koda:', error);
                    
                    // Prikaži poruku o grešci
                    if (typeof toastr !== 'undefined') {
                        toastr.error('Došlo je do greške pri postavljanju primarnog IAF/EAC koda.');
                    } else {
                        alert('Došlo je do greške pri postavljanju primarnog IAF/EAC koda.');
                    }
                    
                    // Vrati dugme u prvobitno stanje
                    $setPrimaryButton.html(originalHtml);
                    $setPrimaryButton.prop('disabled', false);
                }
            });
        } else {
            // Ako je nova kompanija ili kod nema ID, samo ažuriraj lokalne podatke
            iafEacCodesData.forEach(function(c) {
                c.is_primary = false;
            });
            iafEacCodesData[index].is_primary = true;
            
            // Ažuriraj prikaz tabele
            updateIAFEACTable();
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
