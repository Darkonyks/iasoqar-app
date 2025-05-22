/**
 * IAF-EAC Table - Prikaz i manipulacija tabele IAF/EAC kodova
 * Deo reorganizacije frontend koda ISOQAR aplikacije
 */

(function($) {
    'use strict';
    
    // Globalne varijable
    var $table;
    var $tableBody;
    var companyId;
    
    // Inicijalizacija tabele IAF/EAC kodova
    function initIafEacTable() {
        console.log('Inicijalizacija tabele IAF/EAC kodova...');
        
        // Dohvati referencu na tabelu
        $table = $('#iafEacCodesTable');
        $tableBody = $table.find('tbody');
        
        // Dohvati ID kompanije
        companyId = $('#addIafEacButton').data('company-id');
        
        // Učitaj postojeće IAF/EAC kodove
        refreshIafEacTable();
        
        // Dodaj event listener za osvežavanje tabele nakon dodavanja/brisanja
        $(document).on('iaf-eac:changed', function() {
            refreshIafEacTable();
        });
    }
    
    // Funkcija za osvežavanje tabele IAF/EAC kodova
    function refreshIafEacTable() {
        if (!companyId) {
            console.error('Nije pronađen ID kompanije!');
            return;
        }
        
        var url = '/company/api/companies/' + companyId + '/iaf-eac-codes/';
        
        // Ako URL ne postoji, pokušaj alternativni
        var alternativeUrl = '/api/companies/' + companyId + '/iaf-eac-codes/';
        
        // Prikaži indikator učitavanja
        $tableBody.html('<tr><td colspan="5" class="text-center"><i class="fas fa-spinner fa-spin"></i> Učitavanje IAF/EAC kodova...</td></tr>');
        
        // Pokušaj sa prvim URL-om
        $.ajax({
            url: url,
            type: 'GET',
            success: function(response) {
                renderIafEacCodes(response);
            },
            error: function() {
                // Ako prvi URL ne uspe, pokušaj alternativni
                $.ajax({
                    url: alternativeUrl,
                    type: 'GET',
                    success: function(response) {
                        renderIafEacCodes(response);
                    },
                    error: function() {
                        // Ako oba URL-a ne uspeju, koristi podatke iz DOM-a
                        renderIafEacCodesFromDom();
                    }
                });
            }
        });
    }
    
    // Funkcija za renderovanje IAF/EAC kodova iz AJAX odgovora
    function renderIafEacCodes(response) {
        var codes = response.codes || [];
        
        if (codes.length === 0) {
            $tableBody.html('<tr><td colspan="5" class="text-center">Nema dodeljenih IAF/EAC kodova.</td></tr>');
            return;
        }
        
        var html = '';
        
        codes.forEach(function(code) {
            html += generateCodeRow(code);
        });
        
        $tableBody.html(html);
        
        // Inicijalizuj tooltips za dugmad
        $('[data-toggle="tooltip"]').tooltip();
    }
    
    // Funkcija za renderovanje IAF/EAC kodova iz skrivenog polja u DOM-u
    function renderIafEacCodesFromDom() {
        var iafEacCodesData = $('#iaf_eac_codes_data').val();
        var codes = [];
        
        try {
            codes = JSON.parse(iafEacCodesData);
        } catch (e) {
            console.error('Greška pri parsiranju IAF/EAC kodova iz DOM-a:', e);
            $tableBody.html('<tr><td colspan="5" class="text-center">Greška pri učitavanju IAF/EAC kodova.</td></tr>');
            return;
        }
        
        if (codes.length === 0) {
            $tableBody.html('<tr><td colspan="5" class="text-center">Nema dodeljenih IAF/EAC kodova.</td></tr>');
            return;
        }
        
        var html = '';
        
        codes.forEach(function(code) {
            html += generateCodeRow(code);
        });
        
        $tableBody.html(html);
        
        // Inicijalizuj tooltips za dugmad
        $('[data-toggle="tooltip"]').tooltip();
    }
    
    // Funkcija za generisanje HTML reda za IAF/EAC kod
    function generateCodeRow(code) {
        return (
            '<tr data-code-id="' + code.id + '">' +
                '<td>' + code.iaf_code + '</td>' +
                '<td>' + code.description + '</td>' +
                '<td>' + (code.notes || '') + '</td>' +
                '<td>' + generatePrimaryBadge(code.is_primary) + '</td>' +
                '<td class="text-right">' + generateActionButtons(code) + '</td>' +
            '</tr>'
        );
    }
    
    // Funkcija za generisanje bedža za primarni status
    function generatePrimaryBadge(isPrimary) {
        if (isPrimary) {
            return '<span class="badge badge-success">Primarni</span>';
        }
        return '<span class="badge badge-secondary">Sekundarni</span>';
    }
    
    // Funkcija za generisanje dugmadi za akcije
    function generateActionButtons(code) {
        var primaryButton = '';
        
        if (!code.is_primary) {
            primaryButton = 
                '<button type="button" class="btn btn-sm btn-outline-warning set-primary-iaf-eac-btn" ' +
                'data-code-id="' + code.id + '" ' +
                'data-code-name="' + code.iaf_code + '" ' +
                'data-toggle="tooltip" ' +
                'title="Postavi kao primarni">' +
                '<i class="fas fa-star"></i>' +
                '</button> ';
        }
        
        return (
            primaryButton +
            '<button type="button" class="btn btn-sm btn-outline-danger delete-iaf-eac-btn" ' +
            'data-code-id="' + code.id + '" ' +
            'data-code-name="' + code.iaf_code + ' - ' + code.description + '" ' +
            'data-toggle="tooltip" ' +
            'title="Obriši IAF/EAC kod">' +
            '<i class="fas fa-trash"></i>' +
            '</button>'
        );
    }
    
    // Pokretanje inicijalizacije kada je dokument spreman
    $(document).ready(function() {
        initIafEacTable();
    });
    
})(jQuery);
        
        // Učitavanje postojećih IAF/EAC kodova iz DOM-a ili API-ja
        loadExistingIafEacCodes();
    }
    
    // Funkcija za učitavanje postojećih IAF/EAC kodova
    function loadExistingIafEacCodes() {
        var companyId = $('#addIafEacButton').data('company-id');
        if (!companyId) {
            console.error('Nije pronađen ID kompanije!');
            return;
        }
        
        // Ovde možemo implementirati AJAX poziv za dohvatanje kodova,
        // ali za sada ćemo koristiti podatke koji su već učitani u stranicu
        // Tako da nema potrebe za dodatnim zahtevom
        
        // Provera da li postoje IAF/EAC kodovi u hidden input polju
        var iafEacCodesData = $('#iaf_eac_codes_data').val();
        var iafEacCodes = [];
        
        try {
            if (iafEacCodesData && iafEacCodesData !== "[]" && iafEacCodesData !== "") {
                iafEacCodes = JSON.parse(iafEacCodesData);
            }
        } catch (e) {
            console.error('Greška pri parsiranju IAF/EAC kodova:', e);
        }
        
        // Prikaz kodova u tabeli
        renderIafEacCodes(iafEacCodes);
    }
    
    // Funkcija za renderovanje IAF/EAC kodova u tabelu
    function renderIafEacCodes(codes) {
        var $tableBody = $('#iaf-eac-codes-list');
        var $noCodesMessage = $('#no-iaf-codes-message');
        
        // Očisti tabelu
        $tableBody.empty();
        
        if (!codes || codes.length === 0) {
            // Prikaži poruku ako nema kodova
            $noCodesMessage.show();
            return;
        }
        
        // Sakrij poruku
        $noCodesMessage.hide();
        
        // Dodaj svaki kod u tabelu
        codes.forEach(function(code) {
            var statusBadge = code.is_primary 
                ? '<span class="badge badge-success">Primarni</span>' 
                : '<span class="badge badge-secondary">Sekundarni</span>';
            
            var row = `
            <tr>
                <td><strong>${code.iaf_code}</strong></td>
                <td>${code.description}</td>
                <td>${statusBadge}</td>
                <td>${code.notes || '-'}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        ${!code.is_primary ? `
                        <button type="button" class="btn btn-outline-primary set-primary-iaf-eac-btn" 
                                data-code-id="${code.id}" 
                                data-code-name="${code.iaf_code}">
                            <i class="fas fa-star"></i>
                        </button>` : ''}
                        <button type="button" class="btn btn-outline-danger delete-iaf-eac-btn" 
                                data-code-id="${code.id}" 
                                data-code-name="${code.iaf_code}">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </td>
            </tr>
            `;
            
            $tableBody.append(row);
        });
    }
    
    // Funkcija za osvežavanje tabele nakon izmena
    function refreshIafEacTable() {
        loadExistingIafEacCodes();
    }
    
    // Postavljanje javne funkcije za osvežavanje tabele
    window.refreshIafEacTable = refreshIafEacTable;
    
    // Inicijalizacija kada je dokument spreman
    $(document).ready(function() {
        initIafEacTable();
    });
    
})(jQuery);
