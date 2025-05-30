/**
 * JavaScript za rukovanje sesijom i preusmeravanje korisnika
 * Datoteka: session-handler.js
 */

(function($) {
    'use strict';
    
    /**
     * Proverava da li je korisnik prijavljen na osnovu odgovora sa servera
     * @param {Object|string} response - Odgovor sa servera (može biti string ili objekat)
     * @returns {boolean} true ako je korisnik nije prijavljen (odgovor je HTML stranica za prijavu)
     */
    function isLoginPage(response) {
        // Ako je odgovor string, proveri da li sadrži HTML za prijavu
        if (typeof response === 'string') {
            return response.includes('<title>Prijava | ISOQAR</title>') || 
                   response.includes('login-page') ||
                   (response.includes('<form method="post">') && response.includes('csrfmiddlewaretoken'));
        }
        
        // Ako je odgovor objekat koji sadrži HTML (jQuery može parsirati HTML kao objekat)
        if (response && typeof response === 'object' && response.documentElement) {
            const htmlContent = new XMLSerializer().serializeToString(response);
            return htmlContent.includes('<title>Prijava | ISOQAR</title>') || 
                   htmlContent.includes('login-page') ||
                   (htmlContent.includes('<form method="post">') && htmlContent.includes('csrfmiddlewaretoken'));
        }
        
        return false;
    }
    
    /**
     * Rukuje slučajem kada je sesija korisnika istekla
     * Prikazuje poruku i preusmerava korisnika na stranicu za prijavu
     */
    function handleSessionExpired() {
        console.error('Sesija: Korisnik nije prijavljen ili sesija je istekla');
        
        // Prikaži poruku korisniku
        if (typeof toastr !== 'undefined') {
            toastr.error('Niste prijavljeni. Bićete preusmereni na stranicu za prijavu.', '', {
                timeOut: 3000,
                closeButton: true,
                progressBar: true,
                positionClass: 'toast-top-center'
            });
        } else {
            alert('Niste prijavljeni. Bićete preusmereni na stranicu za prijavu.');
        }
        
        // Sačuvaj trenutnu lokaciju da bi se korisnik vratio nakon prijave
        localStorage.setItem('redirectAfterLogin', window.location.href);
        console.log('Sesija: Sačuvana lokacija za preusmeravanje nakon prijave:', window.location.href);
        
        // Preusmeravanje na stranicu za prijavu nakon kratke pauze
        console.log('Sesija: Preusmeravanje na stranicu za prijavu za 3 sekunde...');
        setTimeout(function() {
            console.log('Sesija: Preusmeravanje na stranicu za prijavu...');
            window.location.href = '/accounts/login/';
        }, 3000);
    }
    
    /**
     * Prilagođava jQuery AJAX postavke za detekciju istekle sesije
     */
    function setupAjaxSessionHandling() {
        // Postavi globalni AJAX handler za greške
        $(document).ajaxError(function(event, jqXHR, ajaxSettings, thrownError) {
            // Proveri da li je odgovor HTML stranica za prijavu
            if (jqXHR.responseText && isLoginPage(jqXHR.responseText)) {
                handleSessionExpired();
                return false;
            }
        });
        
        // Postavi globalni AJAX handler za uspešne odgovore
        $(document).ajaxSuccess(function(event, jqXHR, ajaxSettings, data) {
            // Proveri da li je odgovor HTML stranica za prijavu (može se desiti ako server vrati 200 OK)
            if (typeof data === 'string' && isLoginPage(data)) {
                handleSessionExpired();
                return false;
            }
            
            // Proveri da li je odgovor objekat koji sadrži HTML
            if (data && typeof data === 'object' && isLoginPage(data)) {
                handleSessionExpired();
                return false;
            }
        });
        
        // Presretni jQuery.parseJSON da bi detektovali HTML odgovore
        const originalParseJSON = $.parseJSON;
        $.parseJSON = function(data) {
            try {
                // Ako je odgovor HTML stranica za prijavu, rukuj isteklom sesijom
                if (typeof data === 'string' && data.trim().startsWith('<!DOCTYPE html>')) {
                    if (isLoginPage(data)) {
                        handleSessionExpired();
                        // Vrati prazan objekat da bi se izbegla greška parsiranja
                        return {};
                    }
                }
                
                // Inače, koristi originalnu funkciju
                return originalParseJSON.apply(this, arguments);
            } catch (e) {
                // Ako dođe do greške pri parsiranju, proveri da li je odgovor HTML stranica za prijavu
                if (typeof data === 'string' && isLoginPage(data)) {
                    handleSessionExpired();
                    return {};
                }
                
                // Inače, propagiraj grešku
                throw e;
            }
        };
    }
    
    // Inicijalizacija kada je dokument spreman
    $(document).ready(function() {
        console.log('Sesija: Inicijalizacija rukovanja sesijom...');
        setupAjaxSessionHandling();
        
        // Proveri da li postoji parametar za preusmeravanje nakon prijave
        if (localStorage.getItem('redirectAfterLogin') && window.location.pathname === '/accounts/login/') {
            console.log('Sesija: Pronađena lokacija za preusmeravanje nakon prijave:', localStorage.getItem('redirectAfterLogin'));
            
            // Dodaj event listener za uspešnu prijavu
            $('form').on('submit', function() {
                console.log('Sesija: Forma za prijavu poslata, čuvam lokaciju za preusmeravanje');
                // Sačuvaj lokaciju za preusmeravanje u cookie (localStorage može biti nedostupan nakon preusmeravanja)
                document.cookie = 'redirectAfterLogin=' + encodeURIComponent(localStorage.getItem('redirectAfterLogin')) + '; path=/';
            });
        }
    });
    
    // Izloži funkcije globalnom opsegu
    window.sessionHandler = {
        isLoginPage: isLoginPage,
        handleSessionExpired: handleSessionExpired
    };
    
})(jQuery);
