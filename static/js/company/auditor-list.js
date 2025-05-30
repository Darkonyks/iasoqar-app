/**
 * JavaScript za rukovanje funkcionalnostima liste auditora
 * Datoteka: auditor-list.js
 */

$(document).ready(function() {
    'use strict';
    
    // Globalne varijable
    var auditorIdToDelete = null;
    
    /**
     * Inicijalizacija collapse funkcionalnosti za filtere
     */
    function initFilterCollapse() {
        $('.card-header [data-card-widget="collapse"]').click(function() {
            var $cardBody = $(this).closest('.card').find('.card-body');
            if ($cardBody.is(':visible')) {
                $cardBody.slideUp();
                $(this).find('i').removeClass('fa-minus').addClass('fa-plus');
            } else {
                $cardBody.slideDown();
                $(this).find('i').removeClass('fa-plus').addClass('fa-minus');
            }
        });
    }
    
    /**
     * Učitavanje detalja o auditoru za prikaz u modalu za brisanje
     * @param {number} auditorId - ID auditora
     */
    function loadAuditorDetails(auditorId) {
        if (!auditorId) {
            console.error('ID auditora nije definisan');
            return;
        }
        
        // Prikaz indikatora učitavanja
        $('#auditorStandardsContainer').html('<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Učitavanje standarda...</div>');
        
        // AJAX zahtev za dohvatanje detalja o auditoru
        $.ajax({
            url: '/company/api/auditors/' + auditorId + '/details/',
            type: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.success && response.data) {
                    displayAuditorDetails(response.data);
                } else {
                    $('#auditorStandardsContainer').html('<div class="alert alert-warning">Nije moguće učitati standarde.</div>');
                }
            },
            error: function(xhr, status, error) {
                console.error('Greška prilikom učitavanja detalja o auditoru:', error);
                $('#auditorStandardsContainer').html('<div class="alert alert-danger">Došlo je do greške prilikom učitavanja standarda.</div>');
            }
        });
    }
    
    /**
     * Prikaz detalja o auditoru u modalu za brisanje
     * @param {Object} data - Podaci o auditoru
     */
    function displayAuditorDetails(data) {
        // Popunjavanje osnovnih podataka
        $('#auditorDetailName').text(data.name);
        $('#auditorDetailEmail').text(data.email);
        $('#auditorDetailPhone').text(data.phone || '-');
        
        // Prikaz kategorije sa odgovarajućom bojom
        var categoryClass = '';
        switch(data.category) {
            case 'lead_auditor': categoryClass = 'badge-success'; break;
            case 'auditor': categoryClass = 'badge-primary'; break;
            case 'technical_expert': categoryClass = 'badge-secondary'; break;
            case 'trainer': categoryClass = 'badge-info'; break;
            default: categoryClass = 'badge-light';
        }
        
        $('#auditorDetailCategory').html('<span class="badge ' + categoryClass + '">' + data.category_display + '</span>');
        
        // Prikaz standarda i IAF/EAC kodova
        if (data.standards && data.standards.length > 0) {
            var standardsHtml = '';
            
            data.standards.forEach(function(standard) {
                var standardHtml = '<div class="card mb-2">';
                standardHtml += '<div class="card-header bg-light">';
                standardHtml += '<h5 class="mb-0">' + standard.code + ' - ' + standard.name + '</h5>';
                standardHtml += '</div>';
                standardHtml += '<div class="card-body">';
                
                // Datum potpisivanja i napomena
                standardHtml += '<div class="row mb-2">';
                standardHtml += '<div class="col-md-6"><strong>Datum potpisivanja:</strong> ' + (standard.date_signed || '-') + '</div>';
                if (standard.notes) {
                    standardHtml += '<div class="col-md-6"><strong>Napomena:</strong> ' + standard.notes + '</div>';
                }
                standardHtml += '</div>';
                
                // IAF/EAC kodovi
                standardHtml += '<div class="mt-2"><strong>IAF/EAC kodovi:</strong></div>';
                
                if (standard.iaf_eac_codes && standard.iaf_eac_codes.length > 0) {
                    standardHtml += '<div class="mt-1">';
                    standard.iaf_eac_codes.forEach(function(code) {
                        var badgeClass = code.is_primary ? 'badge-primary' : 'badge-light';
                        var primaryIcon = code.is_primary ? '<i class="fas fa-star text-warning ml-1"></i>' : '';
                        
                        standardHtml += '<span class="badge ' + badgeClass + ' mr-1 mb-1" title="' + code.title + '">';
                        standardHtml += code.code + primaryIcon;
                        standardHtml += '</span> ';
                    });
                    standardHtml += '</div>';
                } else {
                    standardHtml += '<div class="text-muted">Nema dodeljenih IAF/EAC kodova</div>';
                }
                
                standardHtml += '</div>'; // card-body
                standardHtml += '</div>'; // card
                
                standardsHtml += standardHtml;
            });
            
            $('#auditorStandardsContainer').html(standardsHtml);
        } else {
            $('#auditorStandardsContainer').html('<div class="alert alert-info">Ovaj auditor nema dodeljenih standarda.</div>');
        }
    }
    
    /**
     * Inicijalizacija modala za brisanje auditora
     */
    function initDeleteModal() {
        // Popunjavanje modala podacima o auditoru koji se briše
        $('.delete-auditor').click(function() {
            auditorIdToDelete = $(this).data('id');
            var auditorName = $(this).data('name');
            $('#auditorNameToDelete').text(auditorName);
            
            // Učitavanje detalja o auditoru
            loadAuditorDetails(auditorIdToDelete);
        });
        
        // Potvrda brisanja auditora
        $('#confirmDeleteAuditor').click(function() {
            console.log('Kliknuto na dugme za potvrdu brisanja');
            
            if (!auditorIdToDelete) {
                console.error('ID auditora za brisanje nije definisan');
                alert('Greška: ID auditora nije definisan');
                return;
            }
            
            console.log('ID auditora za brisanje:', auditorIdToDelete);
            
            var csrfToken = getCsrfToken();
            console.log('CSRF Token:', csrfToken);
            
            // Direktno brisanje bez AJAX-a
            var form = $('<form></form>');
            form.attr('method', 'POST');
            form.attr('action', '/company/auditors/' + auditorIdToDelete + '/delete/');
            
            // Dodavanje CSRF tokena
            var csrfInput = $('<input></input>');
            csrfInput.attr('type', 'hidden');
            csrfInput.attr('name', 'csrfmiddlewaretoken');
            csrfInput.attr('value', csrfToken);
            form.append(csrfInput);
            
            // Dodavanje forme u DOM i slanje
            $('body').append(form);
            form.submit();
            
            // Zatvaranje modala
            $('#deleteAuditorModal').modal('hide');
        });
    }
    
    /**
     * Funkcija za dobijanje CSRF tokena iz kolačića
     * @returns {string} CSRF token
     */
    function getCsrfToken() {
        var name = 'csrftoken';
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Inicijalizacija funkcionalnosti
    initFilterCollapse();
    initDeleteModal();
});
