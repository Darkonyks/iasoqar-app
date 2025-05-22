/**
 * Direct Modal - Direktna implementacija modala bez zavisnosti
 * Deo reorganizacije frontend koda ISOQAR aplikacije
 */

(function() {
    'use strict';
    
    // Kreiranje modala direktno u DOM-u, bez zavisnosti od Bootstrap-a
    function showDirectModal(title, message, type) {
        console.log('Prikazujem direktni modal:', title, message, type);
        
        // Ukloni postojeći modal ako postoji
        removeExistingModal();
        
        // Određivanje klase za tip modala
        var headerClass;
        var iconClass;
        
        switch(type) {
            case 'success':
                headerClass = 'bg-success';
                iconClass = 'fa-check-circle text-success';
                break;
            case 'error':
                headerClass = 'bg-danger';
                iconClass = 'fa-exclamation-circle text-danger';
                break;
            case 'warning':
                headerClass = 'bg-warning';
                iconClass = 'fa-exclamation-triangle text-warning';
                break;
            default:
                headerClass = 'bg-info';
                iconClass = 'fa-info-circle text-info';
        }
        
        // Kreiranje HTML-a za modal
        var modalHTML = `
            <div id="directModal" class="modal" style="display: block; background-color: rgba(0,0,0,0.5); position: fixed; top: 0; left: 0; z-index: 9999; width: 100%; height: 100%; overflow: auto; padding-top: 100px;">
                <div class="modal-dialog" style="max-width: 500px; margin: 30px auto; position: relative;">
                    <div class="modal-content" style="border-radius: 6px; box-shadow: 0 5px 15px rgba(0,0,0,.5);">
                        <div class="modal-header ${headerClass}" style="padding: 15px; border-bottom: 1px solid #e5e5e5; border-radius: 5px 5px 0 0; color: white;">
                            <h5 class="modal-title" style="margin: 0; line-height: 1.42857143;">${title}</h5>
                            <button type="button" class="close" onclick="window.closeDirectModal()" style="background: transparent; border: 0; font-size: 21px; font-weight: 700; opacity: .5; padding: 0; cursor: pointer; float: right;">
                                <span>×</span>
                            </button>
                        </div>
                        <div class="modal-body" style="padding: 15px;">
                            <div style="text-align: center; margin-bottom: 15px;">
                                <i class="fas ${iconClass}" style="font-size: 3rem;"></i>
                            </div>
                            <p style="text-align: center;">${message}</p>
                        </div>
                        <div class="modal-footer" style="padding: 15px; text-align: right; border-top: 1px solid #e5e5e5; border-radius: 0 0 5px 5px;">
                            <button type="button" class="btn btn-primary" onclick="window.closeDirectModal()" style="display: inline-block; margin-bottom: 0; font-weight: 400; text-align: center; white-space: nowrap; vertical-align: middle; -ms-touch-action: manipulation; touch-action: manipulation; cursor: pointer; background-image: none; border: 1px solid transparent; padding: 6px 12px; font-size: 14px; line-height: 1.42857143; border-radius: 4px; -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none; user-select: none; color: #fff; background-color: #007bff; border-color: #007bff;">U redu</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Dodavanje modala u DOM
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Fokusiranje na "U redu" dugme
        setTimeout(function() {
            var okButton = document.querySelector('#directModal .btn-primary');
            if (okButton) {
                okButton.focus();
            }
        }, 100);
        
        console.log('Direktni modal kreiran i prikazan.');
    }
    
    // Funkcija za zatvaranje modala
    function closeDirectModal() {
        console.log('Zatvaranje direktnog modala.');
        removeExistingModal();
    }
    
    // Pomoćna funkcija za uklanjanje postojećeg modala
    function removeExistingModal() {
        var existingModal = document.getElementById('directModal');
        if (existingModal) {
            existingModal.parentNode.removeChild(existingModal);
        }
    }
    
    // Postavljanje funkcija u globalni opseg da budu dostupne
    window.showDirectModal = showDirectModal;
    window.closeDirectModal = closeDirectModal;
})();
