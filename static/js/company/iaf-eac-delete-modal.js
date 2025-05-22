/**
 * IAF-EAC Delete Modal - Funkcionalnost za brisanje IAF/EAC kodova
 * Deo reorganizacije frontend koda ISOQAR aplikacije
 */

(function($) {
    'use strict';
    
    // Varijable za dinamički modal
    var modalId = 'deleteIafEacModal';
    var confirmButtonId = 'confirmDeleteIafEac';
    var cancelButtonId = 'cancelDeleteIafEac';
    
    // Funkcija za inicijalizaciju
    function initIafEacDeleteModal() {
        console.log('Inicijalizacija modala za brisanje IAF/EAC koda...');
        
        // Kreiraj modal za brisanje ako ne postoji
        ensureModalExists();
        
        // Dodaj delegirani event listener za prikazivanje modala
        $(document).on('click', '.delete-iaf-eac-btn', function(e) {
            e.preventDefault();
            showDeleteConfirmationModal($(this));
        });
        
        // Dodaj event listener za potvrdu brisanja
        $(document).on('click', '#' + confirmButtonId, function() {
            var codeId = $(this).data('code-id');
            deleteIafEacCode(codeId);
        });
    }
    
    // Osiguranje da modal za brisanje postoji u DOM-u
    function ensureModalExists() {
        if ($('#' + modalId).length === 0) {
            var modalHTML = `
            <div class="modal fade" id="${modalId}" tabindex="-1" role="dialog" aria-labelledby="${modalId}Label" aria-hidden="true">
              <div class="modal-dialog" role="document">
                <div class="modal-content">
                  <div class="modal-header bg-danger text-white">
                    <h5 class="modal-title" id="${modalId}Label">Potvrda brisanja IAF/EAC koda</h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                      <span aria-hidden="true">&times;</span>
                    </button>
                  </div>
                  <div class="modal-body">
                    <div class="text-center mb-3">
                      <i class="fas fa-exclamation-triangle text-warning" style="font-size: 3rem;"></i>
                    </div>
                    <p>Da li ste sigurni da želite da obrišete IAF/EAC kod <strong id="deleteIafEacCodeName"></strong>?</p>
                    <p class="text-danger">Ova akcija se ne može poništiti.</p>
                  </div>
                  <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" id="${cancelButtonId}" data-dismiss="modal">Odustani</button>
                    <button type="button" class="btn btn-danger" id="${confirmButtonId}" data-code-id="">
                      <i class="fas fa-trash-alt"></i> Obriši IAF/EAC kod
                    </button>
                  </div>
                </div>
              </div>
            </div>
            `;
            
            $('body').append(modalHTML);
            console.log('Kreiran modal za brisanje IAF/EAC koda');
        }
    }
    
    // Funkcija za prikazivanje modala za potvrdu brisanja
    function showDeleteConfirmationModal($button) {
        var codeId = $button.data('code-id');
        var codeName = $button.data('code-name');
        
        console.log('Priprema modala za brisanje IAF/EAC koda:', codeId, codeName);
        
        // Postavi podatke u modal
        $('#deleteIafEacCodeName').text(codeName);
        $('#' + confirmButtonId).data('code-id', codeId);
        
        // Prikaži modal
        $('#' + modalId).modal('show');
    }
    
    // Funkcija za slanje AJAX zahteva za brisanje IAF/EAC koda
    function deleteIafEacCode(codeId) {
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        
        $.ajax({
            url: '/company/api/iaf-eac/delete/',
            type: 'POST',
            data: {
                'code_id': codeId,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                console.log('IAF/EAC kod uspešno obrisan:', response);
                
                // Sakrij modal
                $('#' + modalId).modal('hide');
                
                // Prikaži poruku o uspešnom brisanju
                if (typeof window.showDirectModal === 'function') {
                    window.showDirectModal(
                        'IAF/EAC kod obrisan',
                        response.message,
                        'success'
                    );
                    
                    // Osveži stranicu nakon zatvaranja
                    setTimeout(function() {
                        window.location.reload();
                    }, 1500);
                } else {
                    alert(response.message);
                    window.location.reload();
                }
            },
            error: function(xhr, status, error) {
                console.error('Greška pri brisanju IAF/EAC koda:', error);
                
                // Sakrij modal za potvrdu
                $('#' + modalId).modal('hide');
                
                // Priprema poruke o grešci
                var errorMessage = 'Došlo je do greške pri brisanju IAF/EAC koda.';
                
                try {
                    var response = JSON.parse(xhr.responseText);
                    if (response.message) {
                        errorMessage = response.message;
                    }
                } catch (e) {
                    // Ako nije moguće parsirati odgovor, koristi generičku poruku
                }
                
                // Prikaži poruku o grešci
                if (typeof window.showDirectModal === 'function') {
                    window.showDirectModal(
                        'Greška pri brisanju IAF/EAC koda',
                        errorMessage,
                        'error'
                    );
                } else {
                    alert(errorMessage);
                }
            }
        });
    }
    
    // Pozovi inicijalizaciju kada je dokument spreman
    $(document).ready(function() {
        initIafEacDeleteModal();
    });
    
})(jQuery);
