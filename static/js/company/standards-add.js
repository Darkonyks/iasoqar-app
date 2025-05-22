/**
 * Standards Add - Direktan pristup za dodavanje standarda
 * Deo reorganizacije frontend koda ISOQAR aplikacije
 */

(function($) {
    'use strict';
    
    // Inicijalizacija nakon učitavanja dokumenta
    $(document).ready(function() {
        console.log('Inicijalizacija direktnog pristupa za dodavanje standarda...');
        
        // Zamenjujemo regularnu formu sa AJAX pristupom
        $('#standardAddForm').on('submit', function(e) {
            // Sprečavamo uobičajeno slanje forme
            e.preventDefault();
            
            console.log('Direktan pristup za dodavanje standarda aktiviran');
            
            // Prikupljanje podataka iz forme
            var formData = {
                'standard_definition': $('#standard_definition').val(),
                'issue_date': $('#issue_date').val(),
                'expiry_date': $('#expiry_date').val(),
                'notes': $('#notes').val(),
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            };
            
            // Validacija
            if (!formData.standard_definition) {
                alert('Morate izabrati standard!');
                $('#standard_definition').focus();
                return false;
            }
            
            // Opciona validacija datuma
            if (formData.issue_date && formData.expiry_date) {
                var issueDateObj = new Date(formData.issue_date);
                var expiryDateObj = new Date(formData.expiry_date);
                
                if (expiryDateObj < issueDateObj) {
                    alert('Datum isteka ne može biti pre datuma izdavanja!');
                    $('#expiry_date').focus();
                    return false;
                }
            }
            
            // URL za slanje forme
            var formAction = $(this).attr('action');
            console.log('Slanje AJAX zahteva na:', formAction);
            console.log('Podaci forme:', formData);
            
            // Prikaz indikatora učitavanja
            var submitBtn = $(this).find('button[type="submit"]');
            var originalBtnText = submitBtn.html();
            submitBtn.html('<i class="fas fa-spinner fa-spin"></i> Dodajem...');
            submitBtn.prop('disabled', true);
            
            // Slanje AJAX zahteva
            $.ajax({
                url: formAction,
                type: 'POST',
                data: formData,
                success: function(response) {
                    console.log('Standard uspešno dodat!');
                    
                    // Resetovanje forme
                    $('#standardAddForm')[0].reset();
                    
                    // Dohvati naziv dodatog standarda
                    var standardName = $('#standard_definition option:selected').text();
                    
                    // Pripremi i prikaži modal za uspešno dodavanje
                    $('#successStandardName').text(standardName);
                    $('#standardSuccessModal').modal('show');
                    
                    // Osveži stranicu kada se modal zatvori
                    $('#standardSuccessModal').on('hidden.bs.modal', function () {
                        window.location.reload();
                    });
                },
                error: function(xhr, status, error) {
                    console.error('Greška pri dodavanju standarda:', error);
                    console.error('Status:', xhr.status);
                    console.error('Odgovor:', xhr.responseText);
                    
                    // Priprema teksta greške za prikaz
                    var errorText = 'Status: ' + xhr.status;
                    try {
                        var responseObj = JSON.parse(xhr.responseText);
                        if (responseObj.error) {
                            errorText += '<br>Poruka: ' + responseObj.error;
                        }
                    } catch (e) {
                        errorText += '<br>Odgovor: ' + xhr.responseText;
                    }
                    
                    // Popuni i prikaži modal za grešku
                    $('#errorDetails').html(errorText);
                    $('#standardErrorModal').modal('show');
                    
                    // Resetovanje stanja dugmeta
                    submitBtn.html(originalBtnText);
                    submitBtn.prop('disabled', false);
                }
            });
            
            return false;
        });
        
        // Direktno dodavanje standarda - za testiranje
        $('#directStandardAdd').on('click', function(e) {
            e.preventDefault();
            
            // Prikupljanje URL-a i Company ID-a iz atributa
            var companyId = $(this).data('company-id');
            var addUrl = '/company/companies/' + companyId + '/standards/add/';
            
            // Prikupljanje podataka iz forme
            var formData = {
                'standard_definition': $('#standard_definition').val(),
                'issue_date': $('#issue_date').val(),
                'expiry_date': $('#expiry_date').val(),
                'notes': $('#notes').val(),
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            };
            
            console.log('Direktno dodavanje standarda!');
            console.log('URL:', addUrl);
            console.log('Podaci:', formData);
            
            // Validacija
            if (!formData.standard_definition) {
                alert('Morate izabrati standard!');
                $('#standard_definition').focus();
                return false;
            }
            
            // Slanje AJAX zahteva
            $.ajax({
                url: addUrl,
                type: 'POST',
                data: formData,
                success: function(response) {
                    console.log('Standard uspešno dodat pomoću direktnog dugmeta!');
                    
                    // Dohvati naziv dodatog standarda
                    var standardName = $('#standard_definition option:selected').text();
                    
                    // Pripremi i prikaži modal za uspešno dodavanje
                    $('#successStandardName').text(standardName);
                    $('#standardSuccessModal').modal('show');
                    
                    // Osveži stranicu kada se modal zatvori
                    $('#standardSuccessModal').on('hidden.bs.modal', function () {
                        window.location.reload();
                    });
                },
                error: function(xhr, status, error) {
                    console.error('Greška pri direktnom dodavanju standarda:', error);
                    console.error('Status:', xhr.status);
                    console.error('Odgovor:', xhr.responseText);
                    
                    // Priprema teksta greške za prikaz
                    var errorText = 'Status: ' + xhr.status;
                    try {
                        var responseObj = JSON.parse(xhr.responseText);
                        if (responseObj.error) {
                            errorText += '<br>Poruka: ' + responseObj.error;
                        }
                    } catch (e) {
                        errorText += '<br>Odgovor: ' + xhr.responseText;
                    }
                    
                    // Popuni i prikaži modal za grešku
                    $('#errorDetails').html(errorText);
                    $('#standardErrorModal').modal('show');
                }
            });
        });
    });
    
})(jQuery);
