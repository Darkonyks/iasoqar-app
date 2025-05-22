/**
 * JavaScript za kreiranje i upravljanje modalom za brisanje standarda
 * 
 * Deo reorganizacije frontend koda ISOQAR aplikacije
 */

(function($) {
    'use strict';
    
    // Funkcija za kreiranje modala dinamički
    function createDeleteModal() {
        // Proveri da li modal već postoji
        if ($('#deleteStandardModal').length > 0) {
            console.log('Modal već postoji u DOM-u, neće biti kreiran ponovo.');
            return;
        }
        
        // Kreiraj modal HTML
        var modalHtml = `
            <div class="modal fade" id="deleteStandardModal" tabindex="-1" role="dialog" aria-labelledby="deleteStandardModalLabel" aria-hidden="true">
                <div class="modal-dialog" role="document">
                    <div class="modal-content">
                        <div class="modal-header bg-danger text-white">
                            <h5 class="modal-title" id="deleteStandardModalLabel">Potvrda brisanja standarda</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <p>Da li ste sigurni da želite da obrišete standard <strong id="standardNameToDelete"></strong>?</p>
                            <p class="text-danger"><i class="fas fa-exclamation-triangle"></i> Ova akcija je nepovratna!</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-dismiss="modal">Odustani</button>
                            <form id="deleteStandardForm" method="post" action="">
                                <input type="hidden" name="csrfmiddlewaretoken" value="">
                                <button type="submit" class="btn btn-danger">Obriši</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Dodaj modal na kraj body elementa
        $('body').append(modalHtml);
        
        // Postavi CSRF token
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').first().val();
        $('#deleteStandardForm input[name="csrfmiddlewaretoken"]').val(csrfToken);
        
        console.log('Modal za brisanje standarda je dinamički kreiran i dodat u DOM.');
    }
    
    // Kada je dokument spreman
    $(document).ready(function() {
        console.log('Inicijalizacija dinamičkog modala za brisanje standarda...');
        
        // Kreiraj modal
        createDeleteModal();
        
        // Poveži event handler za dugmad za brisanje
        $(document).on('click', '.btn-delete-standard', function(e) {
            e.preventDefault();
            
            var standardId = $(this).data('standard-id');
            var standardName = $(this).data('standard-name');
            var companyId = $(this).data('company-id');
            
            console.log('Kliknuto brisanje standarda:', standardId, standardName, companyId);
            
            // Postavljanje vrednosti u modalu
            $('#standardNameToDelete').text(standardName);
            
            // Postavljanje URL-a za brisanje
            var deleteUrl = '/company/companies/' + companyId + '/standards/' + standardId + '/delete/';
            $('#deleteStandardForm').attr('action', deleteUrl);
            
            // Prikazivanje modala
            $('#deleteStandardModal').modal('show');
        });
        
        // Kada se modal pojavi
        $(document).on('shown.bs.modal', '#deleteStandardModal', function() {
            console.log('Modal za brisanje standarda je prikazan.');
        });
        
        // Kada se modal zatvori
        $(document).on('hidden.bs.modal', '#deleteStandardModal', function() {
            console.log('Modal za brisanje standarda je zatvoren.');
        });
    });
    
})(jQuery);
