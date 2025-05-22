/**
 * JavaScript za upravljanje standardima kompanije
 * Deo reorganizacije frontend koda ISOQAR aplikacije 
 */

// Funkcija se izvršava kada je DOM spreman
jQuery(document).ready(function($) {
    console.log('Inicijalizacija funkcionalnosti standarda (v2)...');
    
    // Brisanje standarda - direktno povezujemo sa dugmadi
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
    
    // Funkcija za proveru stanja modala
    function checkModalElements() {
        console.log('------ Provera stanja modala ------');
        if ($('#deleteStandardModal').length) {
            console.log('Modal za brisanje POSTOJI');
        } else {
            console.error('Modal za brisanje NE POSTOJI!');
        }
        
        if ($('#standardNameToDelete').length) {
            console.log('Element za ime standarda POSTOJI');
        } else {
            console.error('Element za ime standarda NE POSTOJI!');
        }
        
        if ($('#deleteStandardForm').length) {
            console.log('Forma za brisanje POSTOJI');
        } else {
            console.error('Forma za brisanje NE POSTOJI!');
        }
        console.log('----------------------------------');
    }
    
    // Proveri stanje modala odmah
    checkModalElements();
    
    // Proveri ponovo nakon 1 sekunde kada je DOM sigurno učitan
    setTimeout(checkModalElements, 1000);
});
