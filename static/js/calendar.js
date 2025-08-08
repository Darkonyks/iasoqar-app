// Funkcija koja uklanja duple modalne elemente sa detaljnim logiranjem i boljom proverom
function removeDuplicateModals() {
  console.log('Provera duplikata modalnih prozora...');
  
  // Kompletna lista ID-ova modalnih prozora koje treba proveriti
  const modalIds = [
    'appointmentModal', 
    'appointmentDetailModal', 
    'auditDetailModal', 
    'auditDayModal', 
    'cycleAuditModal',
    'dateChangeConfirmationModal'
  ];
  
  // Brojač uklonjenih modalnih elemenata
  let removedCount = 0;
  
  // Provera dupliranih ID-ova
  modalIds.forEach(modalId => {
    const modals = document.querySelectorAll(`#${modalId}`);
    
    if (modals.length > 1) {
      console.warn(`Pronađeno ${modals.length} elemenata sa ID-om "${modalId}". Uklanjam duplikate.`);
      
      // Zadržimo samo prvi element, uklonimo ostale
      // Prvi element smatramo validnim ako ima kompletnu strukturu
      let validModalIndex = 0;
      
      // Pronalazimo validni modal koji ima potpunu strukturu
      for (let i = 0; i < modals.length; i++) {
        if (modals[i].querySelector('.modal-dialog') && 
            modals[i].querySelector('.modal-content') && 
            modals[i].querySelector('.modal-header')) {
          validModalIndex = i;
          break;
        }
      }
      
      // Uklanjamo sve osim validnog modala
      for (let i = 0; i < modals.length; i++) {
        if (i !== validModalIndex) {
          console.log(`Uklanjam duplikat modala #${modalId}:`, modals[i]);
          modals[i].parentNode.removeChild(modals[i]);
          removedCount++;
        }
      }
    }
  });
  
  // Provera i uklanjanje višestrukih backdrop-ova
  const backdrops = document.querySelectorAll('.modal-backdrop');
  if (backdrops.length > 1) {
    console.warn(`Pronađeno ${backdrops.length} modal backdrop elemenata. Uklanjam višak.`);
    
    // Zadržimo samo jedan backdrop, uklonimo ostale
    for (let i = 1; i < backdrops.length; i++) {
      console.log(`Uklanjam višak backdrop elementa:`, backdrops[i]);
      backdrops[i].parentNode.removeChild(backdrops[i]);
      removedCount++;
    }
  }
  
  // Uklanjanje svih prikazanih modala
  document.querySelectorAll('.modal.show').forEach(modal => {
    // Provera da li je modal trebalo da bude prikazan
    const shouldBeShown = modal.hasAttribute('data-should-be-shown');
    
    if (!shouldBeShown) {
      console.log(`Sakrivam modal koji je inicijalno prikazan:`, modal.id);
      modal.classList.remove('show');
      modal.style.display = 'none';
      modal.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('modal-open');
    }
  });
  
  console.log(`Provera duplikata modalnih prozora završena. Uklonjeno: ${removedCount} elemenata.`);
  
  return removedCount; // Vraćamo broj uklonjenih elemenata za potrebe testiranja
}

// Automatski pokreni proveru kada se dokument učita - poboljšana verzija sa više provera
document.addEventListener('DOMContentLoaded', function() {
  // Sačekaj da se DOM potpuno učita
  setTimeout(function() {
    // Ukloni duple modalne elemente odmah
    const removedCount = removeDuplicateModals();
    console.log(`Inicijalno uklonjeno ${removedCount} dupliranih elemenata.`);
    
    // Popravi modalnu funkcionalnost
    fixModalFunctionality();
    
    // Ponovo proveri nakon kratkog odlaganja u slučaju da se neki elementi dinamički dodaju
    setTimeout(function() {
      removeDuplicateModals();
      // Nakon uklanjanja duplikata, modernizuj bootstrap kontrole
      modernizeBootstrapModals();
      
      // Dodaj globalne handlere za zatvaranje modalnih prozora
      setupModalCloseHandlers();
    }, 500);
  }, 100);
  
  /**
   * Funkcija za postavljanje globalnih handlera za zatvaranje modalnih prozora
   * Ovo osigurava da svi modali mogu biti zatvoreni, bez obzira na verziju Bootstrap-a
   */
  function setupModalCloseHandlers() {
    console.log('Postavljanje globalnih handlera za zatvaranje modalnih prozora...');
    
    // 1. Dodaj handler za Bootstrap 4 način zatvaranja modala
    document.addEventListener('click', function(e) {
      const target = e.target;
      
      // Provera za dugmad sa data-dismiss="modal" (Bootstrap 4)
      if (target.hasAttribute('data-dismiss') && target.getAttribute('data-dismiss') === 'modal') {
        e.preventDefault();
        
        // Pronađi roditeljski modal
        const modal = target.closest('.modal');
        if (modal) {
          console.log('Bootstrap 4 zatvaranje modala:', modal.id);
          safeHideModal(modal);
        }
      }
      
      // Provera za dugmad sa data-bs-dismiss="modal" (Bootstrap 5)
      if (target.hasAttribute('data-bs-dismiss') && target.getAttribute('data-bs-dismiss') === 'modal') {
        e.preventDefault();
        
        // Proveriti da li je modal već zatvoren preko BS5 API-ja
        const modal = target.closest('.modal');
        if (modal && modal.classList.contains('show')) {
          console.log('Bootstrap 5 zatvaranje modala (dodatna provera):', modal.id);
          safeHideModal(modal);
        }
      }
    });
    
    // 2. Dodaj handler za ESC tipku za zatvaranje aktivnog modala
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        const visibleModal = document.querySelector('.modal.show');
        if (visibleModal) {
          console.log('ESC zatvaranje modala:', visibleModal.id);
          safeHideModal(visibleModal);
        }
      }
    });
    
    // 3. Dodaj handler za klik na backdrop (izvan modala)
    document.addEventListener('click', function(e) {
      // Ako je kliknuto direktno na .modal element (ne na njegov sadržaj)
      if (e.target.classList.contains('modal') && e.target.classList.contains('show')) {
        const modalId = e.target.id;
        console.log('Backdrop zatvaranje modala:', modalId);
        safeHideModal(e.target);
      }
    });
    
    console.log('Globalni handleri za zatvaranje modalnih prozora su postavljeni.');
  }
  
  // Postavi observer za praćenje dodavanja novih elemenata
  const targetNode = document.body;
  const config = { childList: true, subtree: true };
  
  // Debounce funkcija - ograničava broj poziva funkcije
  let debounceTimer;
  function debounce(func, delay) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(func, delay);
  }
  
  const observer = new MutationObserver(function(mutationsList) {
    let hasModalChanges = false;
    
    for(const mutation of mutationsList) {
      if (mutation.type === 'childList') {
        // Proveravamo da li su dodani ili uklonjeni modal elementi
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.ELEMENT_NODE) {
            if (node.classList && (node.classList.contains('modal') || node.querySelector('.modal'))) {
              hasModalChanges = true;
              break;
            }
          }
        }
        
        if (!hasModalChanges && mutation.removedNodes.length > 0) {
          for (const node of mutation.removedNodes) {
            if (node.nodeType === Node.ELEMENT_NODE) {
              if (node.classList && (node.classList.contains('modal') || node.querySelector('.modal'))) {
                hasModalChanges = true;
                break;
              }
            }
          }
        }
      }
    }
    
    if (hasModalChanges) {
      // Koristimo debounce da ne pokrećemo funkciju previše često
      debounce(function() {
        console.log('Detektovane promene modalnih elemenata, pokrećem čišćenje...');
        removeDuplicateModals();
      }, 200);
    }
  });
  
  observer.observe(targetNode, config);
  console.log('Observer za modalne prozore je pokrenut');
});

// Funkcija za popravku funkcionalnosti modalnih prozora
function fixModalFunctionality() {
  // Osigurati da su modali inicijalno sakriveni
  document.querySelectorAll('.modal').forEach(modal => {
    modal.style.display = 'none';
    modal.classList.remove('show');
    modal.setAttribute('aria-hidden', 'true');
  });
  
  // Uklanjanje eventualnih zaostalih backdrop-ova
  document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
    backdrop.remove();
  });
  
  // Uklanjanje modal-open klase sa body elementa ako nema prikazanih modala
  if (!document.querySelector('.modal.show')) {
    document.body.classList.remove('modal-open');
  }
}

// Funkcija za sigurno zatvaranje modalnih prozora
function safeHideModal(modalSelector) {
  console.log(`Pokušavam zatvoriti modal: ${modalSelector}`);
  let modalElement;
  
  // Provera da li je selektor string ili DOM element
  if (typeof modalSelector === 'string') {
    modalElement = document.querySelector(modalSelector);
  } else if (modalSelector instanceof Element) {
    modalElement = modalSelector;
  } else if (modalSelector && typeof jQuery !== 'undefined' && modalSelector instanceof jQuery) {
    modalElement = modalSelector[0];
  }
  
  if (!modalElement) {
    console.error(`Modal za zatvaranje nije pronađen: ${modalSelector}`);
    return false;
  }
  
  // Temeljito čišćenje body stila i vraćanje stranice u normalno stanje
  const resetBodyState = () => {
    console.log('Resetovanje stanja stranice...');
    
    // Uklanjanje modal-open klasa
    document.documentElement.classList.remove('modal-open-html');
    document.body.classList.remove('modal-open');
    
    // Vraćanje scrollovanja na prethodnu poziciju ako je sačuvana
    if (document.body.style.top) {
      const scrollY = parseInt((document.body.style.top || '0').replace('px', '')) * -1;
      document.body.style.removeProperty('top');
      document.body.style.removeProperty('width');
      document.body.style.removeProperty('position');
      document.body.style.removeProperty('padding-right');
      document.body.style.removeProperty('overflow');
      window.scrollTo(0, scrollY);
      console.log(`Vraćena pozicija scrollovanja na ${scrollY}px`);
    } else {
      // Ako pozicija nije sačuvana, samo resetuj sve stilove
      document.body.style.removeProperty('padding-right');
      document.body.style.removeProperty('overflow');
      document.body.style.removeProperty('position');
      document.body.style.height = 'auto';
    }
    
    console.log('Vraćeno normalno stanje stranice');
  };
  
  try {
    // Provera verzije Bootstrap-a
    const isBootstrap5 = window.bootstrap && typeof bootstrap.Modal === 'function';
    const isBootstrap4 = window.jQuery && typeof $.fn.modal === 'function';
    
    // Metod 1: Pokušaj sa Bootstrap 5 native API
    if (isBootstrap5) {
      console.log(`Zatvaranje ${modalSelector} korišćenjem Bootstrap 5 API`);
      try {
        const bsModal = typeof bootstrap.Modal.getInstance === 'function'
          ? bootstrap.Modal.getInstance(modalElement)
          : null;
        
        if (bsModal) {
          bsModal.hide();
          
          // Temeljito čišćenje backdrop elemenata i resetovanje stranice nakon kratke pauze
          setTimeout(() => {
            cleanupModalBackdrops(true);
            resetBodyState();
          }, 300);
          return true;
        }
      } catch (bs5Error) {
        console.warn('Ne mogu zatvoriti modal koristeći Bootstrap 5 API:', bs5Error);
        // Nastavi sa drugim metodama
      }
    }
    
    // Metod 2: Pokušaj sa jQuery bootstrap API
    if (isBootstrap4) {
      console.log(`Zatvaranje ${modalSelector} korišćenjem jQuery modal API`);
      try {
        $(modalElement).modal('hide');
        
        // Temeljito čišćenje backdrop elemenata i resetovanje stranice nakon kratke pauze
        setTimeout(() => {
          cleanupModalBackdrops(true);
          resetBodyState();
        }, 300);
        return true;
      } catch (jqError) {
        console.warn('Ne mogu zatvoriti modal koristeći jQuery API:', jqError);
        // Nastavi sa metodom 3
      }
    }
    
    // Metod 3: Manuelno zatvaranje modala
    console.log(`Zatvaranje ${modalSelector} manuelno bez Bootstrap API-ja`);
    modalElement.style.display = 'none';
    modalElement.classList.remove('show');
    modalElement.setAttribute('aria-hidden', 'true');
    
    // Temeljito uklanjanje backdrop-a
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
      backdrop.remove();
    });
    
    // Agresivno čišćenje svih backdrop elemenata
    cleanupModalBackdrops(true);
    
    // Resetovanje stanja stranice
    resetBodyState();
    
    // Proveri da li ima drugih otvorenih modala
    const visibleModals = document.querySelectorAll('.modal.show');
    if (visibleModals.length > 0) {
      console.log(`Pronađeno još ${visibleModals.length} otvorenih modala`);
      // Samo ako zaista ima otvorenih modala, dodaj modal-open klasu
      document.body.classList.add('modal-open');
    }
    
    return true;
  } catch (error) {
    console.error(`Greška pri zatvaranju modala ${modalSelector}:`, error);
    
    // Metod 4: Recovery metod u slučaju greške
    try {
      modalElement.style.display = 'none';
      modalElement.classList.remove('show');
      
      document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
        backdrop.remove();
      });
      
      // Agresivno čišćenje backdrop elemenata i resetovanje stranice
      cleanupModalBackdrops(true);
      resetBodyState();
      return true;
    } catch (finalError) {
      console.error('Konačna greška pri zatvaranju modala:', finalError);
      return false;
    }
  }
}

// Funkcija za konvertovanje Bootstrap 4 modalnih kontrola u Bootstrap 5 format
function modernizeBootstrapModals() {
  console.log('Modernizacija Bootstrap modalnih kontrola...');
  let updatedCount = 0;
  
  // Ažuriranje close dugmadi u header sekcijama
  document.querySelectorAll('.modal .modal-header button.close[data-dismiss="modal"]').forEach(button => {
    console.log('Ažuriranje close dugmeta u headeru:', button);
    button.className = 'btn-close';
    button.removeAttribute('data-dismiss');
    button.setAttribute('data-bs-dismiss', 'modal');
    button.innerHTML = '';
    updatedCount++;
  });
  
  // Ažuriranje dugmadi za zatvaranje u footer sekcijama
  document.querySelectorAll('.modal .modal-footer button[data-dismiss="modal"]').forEach(button => {
    console.log('Ažuriranje dugmeta u footeru:', button);
    button.removeAttribute('data-dismiss');
    button.setAttribute('data-bs-dismiss', 'modal');
    updatedCount++;
  });
  
  // Osiguranje da svi modali imaju ispravne tabindex i ARIA atribute
  document.querySelectorAll('.modal').forEach(modal => {
    if (!modal.hasAttribute('tabindex')) {
      modal.setAttribute('tabindex', '-1');
    }
    
    if (!modal.hasAttribute('aria-labelledby') && modal.querySelector('.modal-title')) {
      const titleId = modal.querySelector('.modal-title').id || `${modal.id}-title`;
      if (!modal.querySelector('.modal-title').id) {
        modal.querySelector('.modal-title').id = titleId;
      }
      modal.setAttribute('aria-labelledby', titleId);
    }
    
    if (!modal.hasAttribute('aria-hidden')) {
      modal.setAttribute('aria-hidden', 'true');
    }
  });
  
  console.log(`Modernizacija završena. Ažurirano ${updatedCount} elemenata.`);
  return updatedCount;
}

// GLOBALNA funkcija za otvaranje modala - dostupna svuda
window.globalOpenModal = function(modalId) {
  console.log('GLOBAL OPEN MODAL:', modalId);
  const modalElement = document.getElementById(modalId);
  if (!modalElement) {
    console.error('Modal sa ID-om', modalId, 'nije pronađen!');
    return false;
  }
  
  // Ukloni aria-hidden atribut
  modalElement.removeAttribute('aria-hidden');
  
  // Dodaj klase i stilove za prikaz
  modalElement.classList.add('show');
  modalElement.style.display = 'block';
  modalElement.style.paddingRight = '17px';
  
  // Dodaj klasu za body
  document.body.classList.add('modal-open');
  
  // Pozovi funkciju za popravku pozicije modala umesto manuelnog kreiranja backdrop-a
  fixModalPosition(modalElement);
  
  // Dodaj event listener za zatvaranje modala
  const closeButtons = modalElement.querySelectorAll('[data-dismiss="modal"]');
  closeButtons.forEach(button => {
    button.addEventListener('click', function() {
      modalElement.classList.remove('show');
      modalElement.style.display = 'none';
      document.body.classList.remove('modal-open');
      const backdrop = document.querySelector('.modal-backdrop');
      if (backdrop) {
        backdrop.parentNode.removeChild(backdrop);
      }
    });
  });
  
  return true;
};

// Funkcija za sigurno prikazivanje modala koja proverava da li je Bootstrap JS učitan
function safeShowModal(modalSelector) {
  console.log(`Pokušavam otvoriti modal (Bootstrap 5): ${modalSelector}`);
  
  try {
    // Ukloni # iz selektora ako postoji
    const modalId = modalSelector.startsWith('#') ? modalSelector.substring(1) : modalSelector;
    const modalElement = document.getElementById(modalId);
    
    // Provera da li modal postoji u DOM-u
    if (!modalElement) {
      console.error(`Modal sa ID-om ${modalId} nije pronađen u DOM-u`);
      alert(`Greška: Modal sa ID-om ${modalId} nije pronađen.`);
      return;
    }
    
    // Proveri da li je Bootstrap 5 dostupan
    if (typeof bootstrap === 'undefined' || typeof bootstrap.Modal === 'undefined') {
      console.warn('Bootstrap 5 JS nije dostupan! Učitavam ga...');
      // Dodaj Bootstrap 5 JS ako nije učitan
      const bootstrapScript = document.createElement('script');
      bootstrapScript.src = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js';
      bootstrapScript.crossOrigin = 'anonymous';
      bootstrapScript.onload = function() {
        console.log('Bootstrap 5 JS uspešno učitan!');
        showBootstrap5Modal(modalElement);
      };
      bootstrapScript.onerror = function() {
        console.error('Greška pri učitavanju Bootstrap 5 JS-a');
        alert('Greška pri učitavanju Bootstrap 5 JS-a. Modal se ne može prikazati.');
      };
      document.head.appendChild(bootstrapScript);
    } else {
      showBootstrap5Modal(modalElement);
    }
  } catch (error) {
    console.error('Greška prilikom prikazivanja modala:', error);
    alert('Došlo je do greške prilikom prikazivanja modala. Pogledajte konzolu za više detalja.');
  }
}

// Funkcija za prikazivanje modala koristeći Bootstrap 5 API
function showBootstrap5Modal(modalElement) {
  try {
    console.log('Prikazujem modal koristeći Bootstrap 5 API');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    // Pozovi funkciju za popravku pozicije modala
    
    setTimeout(() => fixModalPosition(modalElement), 50);
  } catch (error) {
    console.error('Greška pri otvaranju modala koristeći Bootstrap 5 API:', error);
    // Fallback na direktnu DOM manipulaciju
    console.log('Pokušavam otvoriti modal direktnom DOM manipulacijom');
    
    // Ukloni aria-hidden atribut
    modalElement.removeAttribute('aria-hidden');
    
    // Dodaj klase i stilove za prikaz
    modalElement.classList.add('show');
    modalElement.style.display = 'block';
    modalElement.setAttribute('aria-modal', 'true');
    modalElement.setAttribute('role', 'dialog');
    
    // Dodaj klasu za body
    document.body.classList.add('modal-open');
    
    // Pozovi funkciju za popravku pozicije modala umesto manuelnog kreiranja backdrop-a
    fixModalPosition(modalElement);
  }
}

// Funkcija koja proverava CSS stilove modala
function checkModalStyles($modal) {
  const modalElement = $modal[0];
  if (!modalElement) return;
  
  const computedStyle = window.getComputedStyle(modalElement);
  console.log('Modal CSS stilovi:', {
    display: computedStyle.display,
    visibility: computedStyle.visibility,
    opacity: computedStyle.opacity,
    zIndex: computedStyle.zIndex
  });
  
  // Provera problematičnih stilova
  if (computedStyle.display === 'none') {
    console.warn('Modal ima display: none!');
  }
  
  if (computedStyle.visibility === 'hidden') {
    console.warn('Modal ima visibility: hidden!');
  }
  
  if (parseFloat(computedStyle.opacity) === 0) {
    console.warn('Modal ima opacity: 0!');
  }
  
  if (parseInt(computedStyle.zIndex) < 1000) {
    console.warn(`Modal ima nizak z-index: ${computedStyle.zIndex}!`);
  }
}

// Funkcija koja pokušava više metoda za otvaranje modala
function tryMultipleModalOpenMethods($modal) {
  console.log('Pokušavam više metoda za otvaranje modala...');
  
  // Metod 1: Standardni Bootstrap modal API
  try {
    console.log('Metod 1: Standardni Bootstrap modal API');
    // Ukloni aria-hidden atribut pre prikazivanja modala
    $modal.removeAttr('aria-hidden');
    
    // Prikaži modal
    $modal.modal({
      backdrop: 'static',
      keyboard: true,
      focus: true,
      show: true
    });
    
    // Sačuvaj trenutno fokusirani element
    window.lastFocusedElement = document.activeElement;
    
    // Dodaj event listener za zatvaranje modala
    $modal.on('hidden.bs.modal', function() {
      // Vrati fokus na element koji je imao fokus pre otvaranja modala
      if (window.lastFocusedElement) {
        window.lastFocusedElement.focus();
      }
    });
  } catch (e) {
    console.error('Greška u Metodu 1:', e);
  }
  
  // Metod 2: jQuery trigger
  setTimeout(function() {
    try {
      console.log('Metod 2: jQuery trigger');
      $modal.trigger('show.bs.modal');
    } catch (e) {
      console.error('Greška u Metodu 2:', e);
    }
  }, 100);
  
  // Metod 3: Direktno podešavanje CSS-a
  setTimeout(function() {
    try {
      console.log('Metod 3: Direktno podešavanje CSS-a');
      $modal.css({
        'display': 'block',
        'visibility': 'visible',
        'opacity': '1',
        'z-index': '1050'
      });
      
      // Dodaj klase za modal
      $modal.addClass('show');
      $('body').addClass('modal-open');
      
      // Dodaj backdrop ako ne postoji
      if ($('.modal-backdrop').length === 0) {
        $('body').append('<div class="modal-backdrop fade show"></div>');
      }
    } catch (e) {
      console.error('Greška u Metodu 3:', e);
    }
  }, 200);
  
  // Metod 4: Direktan pristup DOM elementu
  setTimeout(function() {
    try {
      console.log('Metod 4: Direktan pristup DOM elementu');
      const modalElement = $modal[0];
      if (modalElement) {
        modalElement.style.display = 'block';
        modalElement.style.visibility = 'visible';
        modalElement.style.opacity = '1';
        modalElement.style.zIndex = '1050';
        modalElement.classList.add('show');
      }
    } catch (e) {
      console.error('Greška u Metodu 4:', e);
    }
  }, 300);
  
  // Metod 5: Fallback - alert ako modal i dalje nije vidljiv
  setTimeout(function() {
    const isVisible = $modal.is(':visible');
    console.log(`Modal vidljivost nakon svih pokušaja: ${isVisible}`);
    
    if (!isVisible) {
      console.warn('Modal nije uspešno prikazan nakon svih pokušaja!');
      
      // Proveri da li je modal u DOM-u
      const modalInDOM = $modal.length > 0;
      console.log(`Modal je još uvek u DOM-u: ${modalInDOM}`);
      
      // Proveri CSS stilove ponovo
      checkModalStyles($modal);
      
      // Pokušaj još jednom sa direktnim show
      try {
        $modal.modal('show');
      } catch (e) {
        console.error('Poslednji pokušaj otvaranja modala nije uspeo:', e);
      }
    }
  }, 500);
}

// Funkcija za formatiranje datuma
function formatDate(dateString) {
  if (!dateString) return 'Nije postavljen';
  
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return 'Neispravan datum';
  
  return date.toLocaleDateString('sr-RS', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
}

// Funkcija za popunjavanje podataka o audit danu u modalnom dijalogu
// Modal se otvara u eventClick handleru direktno u HTML-u
function openAuditDayModal(event) {
  console.log('Popunjavanje podataka za audit day modal:', event);
  console.log('Event extended props:', event.extendedProps);
  
  try {
    // Napomena: Modal se sada otvara u eventClick handleru koristeći Bootstrap 5 API
    // Ova funkcija samo popunjava podatke u već otvorenom modalu
    
    // Postavi učitavanje za sva polja
    $('#audit-title').text('Učitavanje...');
    $('#audit-company').text('Učitavanje...');
    $('#audit-date').text('Učitavanje...');
    $('#audit-auditor').text('Učitavanje...');
    $('#audit-status').text('Učitavanje...');
    $('#audit-description').text('Učitavanje...');
    
    // Dobavi podatke iz event objekta
    const eventProps = event.extendedProps || {};
    const auditId = eventProps.audit_id;
    const auditDayId = eventProps.audit_day_id;
    
    console.log('Audit ID from event:', auditId);
    console.log('Audit Day ID from event:', auditDayId);
    
    if (!auditId && !auditDayId) {
      console.error('Nije pronađen ID audita ili audit dana u event objektu');
      $('#audit-title').text('Greška: Nije pronađen ID audita');
      return;
    }
    
    // Proveri da li je ovo zaista audit_day događaj
    const eventType = event.extendedProps?.type || event.extendedProps?.eventType;
    if (eventType !== 'audit_day') {
      console.warn('Događaj nije tipa audit_day, ali je pozvana funkcija openAuditDayModal');
    }
    
    if (!auditId) {
      console.error('Nije pronađen ID audita u event objektu');
      $('#audit-title').text('Greška: Nije pronađen ID audita');
      $('#audit-day-date').text('Greška: Nije pronađen ID audita');
      $('#audit-day-is-planned').text('Nije dostupno');
      $('#audit-day-is-actual').text('Nije dostupno');
      $('#audit-day-notes').text('Nije dostupno');
      $('#editAuditDayBtn').prop('disabled', true);
      return;
    }
    
    // Popuni osnovne podatke iz event objekta koje već imamo
    $('#audit-day-date').text(formatDate(event.start) || 'N/A');
    $('#audit-day-audit-id').text(auditId || 'N/A');
    
    // Dohvati detaljne podatke o audit danu preko API-ja
    const apiUrl = `/company/api/audit-days/by-audit/${auditId}/`;
    console.log('AJAX URL for audit day data:', apiUrl);
    console.log('Event data being sent:', {
      eventId: event.id,
      eventStart: event.start,
      eventProps: event.extendedProps,
      auditId: auditId
    });
    
    // Dodaj timestamp za praćenje vremena izvršavanja
    const requestStartTime = new Date().getTime();
    
    $.ajax({
      url: apiUrl,
      method: 'GET',
      dataType: 'json',
      timeout: 10000, // 10 sekundi timeout
      beforeSend: function(xhr) {
        console.log('Sending AJAX request with headers:', xhr.getAllResponseHeaders());
      },
      success: function(data) {
        const requestEndTime = new Date().getTime();
        console.log('=== AJAX Success ===');
        console.log('Request duration:', requestEndTime - requestStartTime, 'ms');
        console.log('Raw response:', data);
        console.log('Full response (stringified):', JSON.stringify(data, null, 2));
        
        if (data && data.audit) {
          console.log('Audit object structure:', {
            hasAuditDays: !!data.audit.audit_days,
            auditDaysType: typeof data.audit.audit_days,
            auditDaysLength: data.audit.audit_days ? data.audit.audit_days.length : 0,
            auditDays: data.audit.audit_days
          });
        }
        
        if (!data.audit) {
          console.error('Nema audit objekta u odgovoru');
          showAuditDayError('Nema podataka o auditu');
          return;
        }
        
        console.log('Audit object keys:', Object.keys(data.audit));
        
        if (!Array.isArray(data.audit.audit_days)) {
          console.error('audit_days nije niz:', data.audit.audit_days);
          showAuditDayError('Neispravan format audit dana');
          return;
        }
        
        console.log('Audit days array:', JSON.stringify(data.audit.audit_days, null, 2));
        console.log('Number of audit days:', data.audit.audit_days.length);
        
        if (data.audit.audit_days.length > 0) {
          const firstDay = data.audit.audit_days[0];
          console.log('First audit day:', JSON.stringify(firstDay, null, 2));
          console.log('First audit day ID:', firstDay.id);
          console.log('First audit day date:', firstDay.date);
          console.log('Audit days IDs:', data.audit.audit_days.map(day => day.id));
        } else {
          console.warn('Nema audit dana u nizu');
        }
        
        if (!data) {
          console.error('Prazan odgovor od servera');
          return;
        }
        
        if (!data.success) {
          console.error('Server je vratio grešku:', data);
          return;
        }
        
        if (!data.audit) {
          console.error('Nema podataka o auditu u odgovoru');
          return;
        }
        
        if (!data.audit.audit_days || data.audit.audit_days.length === 0) {
          console.error('Nema audit dana u odgovoru');
          return;
        }
        
        console.log('Pozivam updateAuditDayModal sa podacima...');
        updateAuditDayModal(data, event);
      },
      error: function(xhr, status, error) {
        console.error('Greška prilikom dohvatanja podataka o audit danu:', error);
        console.error('Status:', status);
        console.error('Response text:', xhr.responseText);
        
        // Pokušaj da koristimo podatke iz event objekta ako su dostupni
        $('#audit-day-is-planned').text(eventProps.is_planned ? 'Da' : 'Ne');
        $('#audit-day-is-actual').text(eventProps.is_actual ? 'Da' : 'Ne');
        $('#audit-day-notes').text(eventProps.notes || 'Nema napomena');
        
        // Prikaži grešku
        let errorMsg = 'Greška prilikom dohvatanja podataka';
        try {
          const response = JSON.parse(xhr.responseText);
          if (response && response.error) {
            errorMsg = response.error;
          }
        } catch (e) {
          console.error('Greška prilikom parsiranja odgovora:', e);
        }
        
        alert('Greška prilikom dohvatanja podataka o audit danu: ' + errorMsg);
      }
    });
    
    // Postavi URL za dugme za pregled audita
    $('#viewAuditBtn').off('click').on('click', function() {
      if (auditId) {
        const auditUrl = `/company/audits/${auditId}/`;
        console.log('Navigating to audit URL:', auditUrl);
        window.location.href = auditUrl;
      } else {
        alert('ID audita nije dostupan.');
      }
    });
  } catch (e) {
    console.error('Greška pri otvaranju AuditDay modala:', e);
  }
}

// Funkcija za ažuriranje modala sa podacima o audit danu
function updateAuditDayModal(data, event) {
  try {
    // Detaljno logovanje primljenih podataka
    console.log('Raw audit day data:', JSON.stringify(data, null, 2));
    console.log('Event:', event);
    console.log('Event date:', event.start);
    
    // Validacija osnovnih podataka
    if (!data || !data.success || !data.audit) {
      console.error('Neispravan format podataka:', data);
      showAuditDayError('Neispravan format podataka');
      return;
    }
    
    // Validacija datuma događaja
    if (!event.start || !(event.start instanceof Date)) {
      console.error('Neispravan datum događaja:', event.start);
      showAuditDayError('Neispravan datum događaja');
      return;
    }
    
    // Validacija audit dana
    const { audit } = data;
    console.log('Full audit data:', JSON.stringify(audit, null, 2));
    console.log('Audit data:', audit);
    
    if (!audit.audit_days) {
      console.error('Nema audit_days niza u odgovoru');
      showAuditDayError('Nema audit dana u odgovoru');
      return;
    }
    
    if (!Array.isArray(audit.audit_days)) {
      console.error('audit_days nije niz:', audit.audit_days);
      showAuditDayError('Neispravan format audit dana');
      return;
    }
    
    if (audit.audit_days.length === 0) {
      console.error('Nema audit dana u odgovoru (prazan niz)');
      showAuditDayError('Nema audit dana u odgovoru');
      return;
    }
    
    // Popuni osnovne podatke o auditu
    $('#audit-company').text(audit.company_name || 'N/A');
    $('#audit-type').text(audit.audit_type_display || 'N/A');
    $('#audit-status').text(audit.audit_status_display || 'N/A');
    $('#audit-planned-date').text(formatDate(audit.planned_date) || 'Nije postavljen');
    $('#audit-actual-date').text(formatDate(audit.actual_date) || 'Nije postavljen');
    
    // Filtriraj validne audit dane i logiraj rezultate
    const validAuditDays = audit.audit_days.filter(day => {
      const isValid = day && day.id && day.date;
      if (!isValid) {
        console.warn('Nevažeći audit dan:', day);
      }
      return isValid;
    });
    
    console.log('Valid audit days:', validAuditDays);
    
    if (validAuditDays.length === 0) {
      console.error('Nijedan audit dan nema validan ID i datum');
      showAuditDayError('Nema validnih audit dana u odgovoru');
      return;
    }
    
    // Pronađi odgovarajući audit dan
    const eventYear = event.start.getFullYear();
    const eventMonth = event.start.getMonth();
    const eventDay = event.start.getDate();
    
    console.log(`Tražim audit dan za datum: ${eventYear}-${eventMonth + 1}-${eventDay}`);
    
    let selectedAuditDay = validAuditDays.find(day => {
      try {
        const dayDate = new Date(day.date);
        const matches = dayDate.getFullYear() === eventYear &&
                       dayDate.getMonth() === eventMonth &&
                       dayDate.getDate() === eventDay;
        
        console.log(`Poređenje datuma:`, {
          auditDay: day.date,
          parsedDate: dayDate,
          eventDate: event.start,
          matches: matches
        });
        
        return matches;
      } catch (e) {
        console.warn('Greška pri parsiranju datuma za audit dan:', e, day);
        return false;
      }
    });
    
    // Ako nema poklapanja po datumu, uzmi prvi validan
    if (!selectedAuditDay) {
      console.warn('Nije pronađen audit dan za tačan datum, koristim prvi dostupan');
      selectedAuditDay = validAuditDays[0];
    }
    
    console.log('Selected audit day:', selectedAuditDay);
    
    // Ažuriraj modal sa podacima o danu audita
    $('#audit-day-is-planned').text(selectedAuditDay.is_planned ? 'Da' : 'Ne');
    $('#audit-day-is-actual').text(selectedAuditDay.is_actual ? 'Da' : 'Ne');
    $('#audit-day-notes').text(selectedAuditDay.notes || 'Nema napomena');
    
    // Podesi dugme za izmenu
    $('#editAuditDayBtn')
      .prop('disabled', false)
      .off('click')
      .on('click', function() {
        const auditDayUrl = `/company/audit-days/${selectedAuditDay.id}/update/`;
        console.log('Navigating to audit day update URL:', auditDayUrl);
        window.location.href = auditDayUrl;
      });
  } catch (e) {
    console.error('Greška pri ažuriranju AuditDay modala:', e);
    showAuditDayError(`Greška: ${e.message}`);
  }
}

// Pomoćna funkcija za prikazivanje greške u modalu
function showAuditDayError(errorMessage) {
  $('#audit-day-is-planned').text('Greška');
  $('#audit-day-is-actual').text('Greška');
  $('#audit-day-notes').text(errorMessage || 'Došlo je do greške');
  $('#editAuditDayBtn').prop('disabled', true);
}

// Funkcija za otvaranje modala za detalje nadzorne provere (iz Python backend API-ja)
function openCycleAuditModal(event) {
  console.log('Opening cycle audit modal for event:', event);
  
  try {
    // Prikaži osnovne podatke o događaju za debugging
    const eventStr = JSON.stringify(event, function(key, value) {
      // Handle circular references
      if (key === 'source' || key === 'sourceId') return '[CIRCULAR]';
      return value;
    }, 2);
    console.log('Event data structure:', eventStr);
    
    // Postavi učitavanje za sva polja
    $('#cycle-company').text('Učitavanje...');
    $('#cycle-audit-type').text('Učitavanje...');
    $('#cycle-status').text('Učitavanje...');
    $('#cycle-planned-date').text('Učitavanje...');
    $('#cycle-actual-date').text('Učitavanje...');
    $('#cycle-id').text('Učitavanje...');
    $('#cycle-start-date').text('Učitavanje...');
    $('#cycle-end-date').text('Učitavanje...');
    $('#cycle-cycle-status').text('Učitavanje...');
    $('#cycle-notes').text('Učitavanje...');
    
    // Izvuci audit ID iz event objekta na više načina
    let auditId = extractAuditId(event);
    
    if (!auditId) {
      console.error('Nije pronađen ID audita u event objektu');
      showCycleAuditError('Nije moguće identifikovati audit iz događaja u kalendaru.');
      return;
    }
    
    console.log('Extracted Audit ID from event:', auditId);
    
    // Postavi URL za API zahtev
    const apiUrl = `/company/api/supervision-audit/${auditId}/`;
    console.log('Calling API endpoint:', apiUrl);
    
    // Pripremi AJAX zahtev za dohvatanje podataka sa backend-a
    $.ajax({
      url: apiUrl,
      type: 'GET',
      dataType: 'json',
      headers: {
        'X-CSRFToken': getCsrfToken()
      },
      success: function(response) {
        console.log('API response success:', response);
        
        if (!response.success) {
          console.error('API returned error:', response.message);
          showCycleAuditError(response.message || 'Došlo je do greške prilikom dohvatanja podataka.');
          return;
        }
        
        // Dobavljeni podaci sa backend-a
        const audit = response.audit;
        const cycle = response.cycle;
        const company = response.company;
        
        // Popuni informacije o kompaniji
        $('#cycle-company').text(company.name);
        
        // Popuni informacije o auditu
        $('#cycle-audit-type').text(audit.audit_type_display || 'Nije definisano');
        $('#cycle-status').text(audit.audit_status_display || 'Nije definisano');
        $('#cycle-planned-date').text(formatDate(audit.planned_date) || 'Nije definisano');
        $('#cycle-actual-date').text(formatDate(audit.actual_date) || 'Nije definisano');
        $('#cycle-notes').text(audit.notes || 'Nema napomena');
        
        // Postavi ID audita na dugme za izmenu
        if (audit.id) {
          $('#editAuditBtn').prop('disabled', false).data('audit-id', audit.id);
        } else {
          $('#editAuditBtn').prop('disabled', true);
        }
        
        // Popuni informacije o ciklusu
        $('#cycle-id').text(cycle.id || 'N/A');
        $('#cycle-start-date').text(formatDate(cycle.start_date) || 'Nije definisano');
        $('#cycle-end-date').text(formatDate(cycle.end_date) || 'Nije definisano');
        $('#cycle-cycle-status').text(cycle.status_display || 'Nije definisano');
        
        // Postavi URL za dugme za pregled ciklusa
        $('#viewCycleBtn').off('click').on('click', function() {
          window.location.href = `/company/cycles/${cycle.id}/`;
        }).prop('disabled', !cycle.id);
        
        // Postavi URL za dugme za izmenu audita
        $('#editAuditBtn').off('click').on('click', function() {
          window.location.href = `/company/cycles/${cycle.id}/audits/${audit.id}/update/`;
        }).prop('disabled', !audit.id);
        
        // Osiguraj da se modal prikaže
        try {
          showModal('#cycleAuditModal');
        } catch (e) {
          console.error('Error showing modal:', e);
        }
      },
      error: function(xhr, status, error) {
        console.error('API error:', error);
        console.error('Status:', status);
        console.error('Response:', xhr.responseText);
        showCycleAuditError('Greška pri dohvatanju podataka sa servera: ' + error);
      }
    });
    
  } catch (e) {
    console.error('Greška pri otvaranju CycleAudit modala:', e);
    showCycleAuditError(`Neočekivana greška: ${e.message}`);
  }
}

// Pomoćna funkcija za prikazivanje greške u modalu za nadzornu proveru
function showCycleAuditError(errorMessage) {
  // Postavi poruku greške i osiguraj da se modal prikaže
  $('#cycle-company').text('Greška');
  $('#cycle-audit-type').text('Greška');
  $('#cycle-status').text('Greška');
  $('#cycle-notes').text(errorMessage || 'Došlo je do greške pri učitavanju podataka');
  $('#cycle-id').text('N/A');
  $('#cycle-start-date').text('N/A');
  $('#cycle-end-date').text('N/A');
  $('#cycle-cycle-status').text('N/A');
  $('#cycle-planned-date').text('N/A');
  $('#cycle-actual-date').text('N/A');
  
  // Onemogući dugmad
  $('#viewCycleBtn').prop('disabled', true);
  $('#editAuditBtn').prop('disabled', true);
  
  // Osiguraj da se modal prikaže
  try {
    showModal('#cycleAuditModal');
  } catch (e) {
    console.error('Error showing error modal:', e);
  }
}

// Pomoćna funkcija za izvlačenje audit ID iz event objekta
function extractAuditId(event) {
  let auditId = null;
  
  // Pomoćna funkcija za izvlačenje ID-a iz string formata
  function extractIdFromString(str) {
    if (!str) return null;
    
    // Check for common formats like 'audit_123' or just '123'
    if (str.includes('audit_')) {
      return str.split('audit_').pop();
    } else if (str.includes('_')) {
      return str.split('_').pop();
    } else if (!isNaN(parseInt(str))) {
      return str;
    }
    return null;
  }
  
  // 1. Try from extendedProps
  if (event.extendedProps) {
    const props = event.extendedProps;
    auditId = props.audit_id || props.auditId || props.id;
  }
  
  // 2. Try from event._def.extendedProps
  if (!auditId && event._def && event._def.extendedProps) {
    const defProps = event._def.extendedProps;
    auditId = defProps.audit_id || defProps.auditId || defProps.id;
  }
  
  // 3. Try from event.id
  if (!auditId && event.id) {
    auditId = extractIdFromString(event.id);
  }
  
  // 4. Try from event._def.publicId
  if (!auditId && event._def && event._def.publicId) {
    auditId = extractIdFromString(event._def.publicId);
  }
  
  // 5. Scan all properties for anything containing 'audit' and 'id'
  if (!auditId) {
    Object.keys(event).forEach(key => {
      if (key.toLowerCase().includes('id') || key.toLowerCase().includes('audit')) {
        const potentialId = extractIdFromString(event[key]);
        if (potentialId) {
          console.log('Found potential audit ID in property:', key, potentialId);
          auditId = potentialId;
        }
      }
    });
  }
  
  return auditId;
}

// Funkcija za otvaranje modala za detalje termina
function openAppointmentModal(event) {
  console.log('Opening appointment modal for event:', event);
  
  try {
    // Dump ENTIRE event object as string for full inspection
    const eventStr = JSON.stringify(event, function(key, value) {
      // Handle circular references
      if (key === 'source' || key === 'sourceId') return '[CIRCULAR]';
      return value;
    }, 2);
    console.log('Full event data structure:', eventStr);
    
    // Set loading state
    $('#appointment-title').text('Učitavanje...');
    $('#appointment-company').text('Učitavanje...');
    $('#appointment-start').text('Učitavanje...');
    $('#appointment-end').text('Učitavanje...');
    $('#appointment-location').text('Učitavanje...');
    $('#appointment-description').text('Učitavanje...');
    $('#appointment-contacts').text('Učitavanje...');
    
    // FULLCALENDAR 6 EVENT STRUCTURE - Based on actual log analysis
    let appointmentId = null;
    let title = 'Nepoznat termin';
    let company = 'Nepoznata kompanija';
    let startDate = null;
    let endDate = null;
    let location = 'Nepoznata lokacija';
    let description = 'Nema opisa';
    let contacts = [];
    
    // Extract data from the FullCalendar 6 event structure
    if (event) {
      // Direct ID access first
      if (event.id) appointmentId = event.id;
      
      // Handle native FullCalendar structure
      if (event._def) {
        // Event ID is in publicId
        appointmentId = event._def.publicId || appointmentId;
        
        // Title is in title
        title = event._def.title || title;
        
        // Extended props contain all custom data
        if (event._def.extendedProps) {
          const props = event._def.extendedProps;
          company = props.company || company;
          location = props.location || location;
          description = props.description || description;
          
          // Various ID locations
          if (!appointmentId) {
            appointmentId = props.appointment_id || props.id || props.appointmentId || appointmentId;
          }
          
          // Handle contacts in various formats
          if (props.contacts) {
            if (Array.isArray(props.contacts)) {
              contacts = props.contacts;
            } else if (typeof props.contacts === 'string') {
              contacts = [props.contacts];
            }
          }
        }
        
        // Extract dates from the instance range
        if (event._instance && event._instance.range) {
          startDate = event._instance.range.start;
          endDate = event._instance.range.end;
        }
      }
      // Handle normalized event data (might be passed directly)
      else {
        title = event.title || title;
        
        if (event.extendedProps) {
          const props = event.extendedProps;
          company = props.company || company;
          location = props.location || location;
          description = props.description || description;
          
          if (!appointmentId) {
            appointmentId = props.appointment_id || props.id || props.appointmentId || appointmentId;
          }
          
          if (props.contacts) {
            if (Array.isArray(props.contacts)) {
              contacts = props.contacts;
            } else if (typeof props.contacts === 'string') {
              contacts = [props.contacts];
            }
          }
        }
        
        // Direct date access
        startDate = event.start || startDate;
        endDate = event.end || endDate;
      }
    }
    
    // FixMe: Fallback to using event directly as a data source if needed
    if (!appointmentId) {
      // Last resort - try to extract from any property that might contain 'id'
      Object.keys(event).forEach(key => {
        if (key.toLowerCase().includes('id') && !appointmentId) {
          console.log('Found potential ID in property:', key, event[key]);
          appointmentId = event[key];
        }
      });
    }
    
    console.log('Extracted appointment data:', {
      id: appointmentId,
      title: title,
      company: company,
      startDate: startDate,
      endDate: endDate,
      location: location,
      contacts: contacts
    });
    
    // Still no ID? Generate one from the title and date as fallback
    if (!appointmentId && title) {
      appointmentId = 'generated_' + title.replace(/\s+/g, '_').toLowerCase() + '_' + Date.now();
      console.log('Generated fallback ID:', appointmentId);
    }
    
    // Handle missing ID - should be very rare now with our fallback
    if (!appointmentId) {
      console.error('Nije pronađen ID termina u event objektu');
      $('#appointment-title').text('Greška: Nije pronađen ID termina');
      return;
    }
    
    // Fill basic data from event object
    $('#appointment-title').text(title || 'Bez naslova');
    $('#appointment-company').text(company || 'Nije definisano');
    
    // Format dates safely
    if (startDate) {
      $('#appointment-start').text(formatDate(startDate) + ' ' + (startDate instanceof Date ? startDate.toLocaleTimeString('sr-RS') : ''));
    } else {
      $('#appointment-start').text('Nije definisano');
    }
    
    if (endDate) {
      $('#appointment-end').text(formatDate(endDate) + ' ' + (endDate instanceof Date ? endDate.toLocaleTimeString('sr-RS') : ''));
    } else {
      $('#appointment-end').text('Nije definisano');
    }
    
    // Set other fields
    $('#appointment-location').text(location || 'Nije definisano');
    $('#appointment-description').text(description || 'Nema opisa');
    
    // Handle contacts array or string
    if (contacts && contacts.length > 0) {
      $('#appointment-contacts').text(contacts.join(', '));
    } else {
      $('#appointment-contacts').text('Nema kontakata');
    }
    
    // Set ID for edit button and hidden input
    $('#appointmentId').val(appointmentId);
    $('#editAppointmentBtn').data('id', appointmentId);

    // Display modal with multiple fallback methods
    try {
      console.log('Attempting to show modal using window.showModal');
      if (typeof window.showModal === 'function') {
        window.showModal('#appointmentModal');
      } else if (typeof bootstrap !== 'undefined') {
        console.log('Falling back to bootstrap.Modal directly');
        const modalElement = document.querySelector('#appointmentModal');
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
      } else if (typeof $ !== 'undefined') {
        console.log('Falling back to jQuery modal');
        $('#appointmentModal').modal('show');
      } else {
        console.log('Using manual DOM manipulation as last resort');
        const modalElement = document.querySelector('#appointmentModal');
        modalElement.classList.add('show');
        modalElement.style.display = 'block';
        document.body.classList.add('modal-open');
      }
    } catch (modalError) {
      console.error('Failed to show modal:', modalError);
      // Ultimate fallback
      try {
        const modalElement = document.querySelector('#appointmentModal');
        modalElement.classList.add('show');
        modalElement.style.display = 'block';
      } catch (e) {
        console.error('Even fallback failed:', e);
      }
    }
  } catch (error) {
    console.error('Error in openAppointmentModal:', error);
  }
}

// Funkcija za direktno otvaranje audit day modala
function openAuditDayModalDirectly() {
  console.log('Direktno otvaranje audit day modala');
  const modalEl = document.getElementById('auditDetailModal');
  
  if (!modalEl) {
    console.error('Modal element #auditDetailModal nije pronađen!');
    alert('Greška: Modal za audit nije pronađen.');
    return;
  }

  // Resetuj sve stilove modala pre otvaranja
  resetModalStyles(modalEl);
  
  try {
    // Tradicionalan način otvaranja Bootstrap modala
    const auditModal = new bootstrap.Modal(modalEl, {
      backdrop: true,
      keyboard: true,
      focus: true
    });
    
    // Prikaži modal
    auditModal.show();
    console.log('Modal uspešno otvoren');
    
    // Popravi pozicioniranje nakon otvaranja
    setTimeout(() => {
      fixModalPosition(modalEl);
    }, 50);
  } catch (err) {
    console.error('Greška pri otvaranju modala:', err);
    
    // Rezervni način - jQuery
    $(modalEl).modal('show');
    
    // Takođe popravi pozicioniranje
    setTimeout(() => {
      fixModalPosition(modalEl);
    }, 50);
  }
}

// Funkcija za popravljanje modal backdrop problema
function fixModalBackdropIssue() {
  console.log('Popravljanje modal-backdrop problema');
  
  // 1. Pronađimo sve .modal-backdrop elemente 
  const backdrops = document.querySelectorAll('.modal-backdrop');
  console.log(`Pronađeno ${backdrops.length} backdrop elemenata`);
  
  // 2. Radikalno rešenje - kompletno uklanjanje backdrop-a
  backdrops.forEach(backdrop => {
    console.log('Uklanjanje backdrop elementa');
    try {
      backdrop.parentNode.removeChild(backdrop);
    } catch (e) {
      console.error('Greška pri uklanjanju backdrop elementa:', e);
    }
  });
  
  // 3. Osigurajmo da modalni dijalozi imaju ekstremno visoki z-index
  document.querySelectorAll('.modal').forEach(modal => {
    modal.style.zIndex = '9999';
    console.log('Postavljen ekstremni z-index za modal:', modal);
    
    // Kreiranje našeg custom backdrop-a
    createCustomBackdrop(modal);
  });
  
  // 4. Dodatno povećamo z-index za sadržaj modala
  document.querySelectorAll('.modal-dialog, .modal-content').forEach(element => {
    element.style.zIndex = '10000';
    element.style.position = 'relative';
    console.log('Postavljen ekstremni z-index za element:', element);
  });
}

// Funkcija za resetovanje svih stilova modala na podrazumevane vrednosti
function resetModalStyles(modalElement) {
  console.log('Resetovanje stilova za modal');
  
  // Resetuj stil samog modala
  modalElement.style = '';
  modalElement.removeAttribute('style');
  
  // Resetuj stilove modal-dialog elementa
  const dialogElement = modalElement.querySelector('.modal-dialog');
  if (dialogElement) {
    dialogElement.style = '';
    dialogElement.removeAttribute('style');
    dialogElement.classList.add('modal-dialog-centered'); // Dodaj klasu za centriranje
  }
  
  // Resetuj stilove modal-content elementa
  const contentElement = modalElement.querySelector('.modal-content');
  if (contentElement) {
    contentElement.style = '';
    contentElement.removeAttribute('style');
  }
  
  // Ukloni sve custom backdrop elemente
  const customBackdrops = document.querySelectorAll('#custom-modal-backdrop');
  customBackdrops.forEach(backdrop => {
    if (backdrop && backdrop.parentNode) {
      backdrop.parentNode.removeChild(backdrop);
    }
  });
  
  console.log('Stilovi modala su resetovani');
}

// Neutralizacija stacking context-a na body i wrapper elementima
function neutralizeBodyForModal() {
  console.log('Neutralizacija konteksta za modalni prozor');

  // Resetuj kritične stilove na body
  document.body.style.position = 'static';
  document.body.style.zIndex = 'auto';
  document.body.style.pointerEvents = 'auto';
  document.body.style.transform = '';
  document.body.style.background = '';
  document.body.style.boxShadow = '';

  // Resetuj stacking context i pointer-events na ključnim layout elementima
  document.querySelectorAll('.wrapper, .main-header, .main-sidebar, .content-wrapper, nav, header, aside').forEach(el => {
    el.style.position = 'static';
    el.style.zIndex = 'auto';
    el.style.pointerEvents = 'auto';
    el.style.transform = '';
    el.style.background = '';
    el.style.boxShadow = '';
  });

  // Osiguraj da modal i modal-dialog elementi budu u fokusu sa najvišim z-index
  setTimeout(() => {
    document.querySelectorAll('.modal').forEach(modal => {
      modal.style.position = 'fixed';
      modal.style.zIndex = '9999';
      modal.style.display = 'block';
      modal.style.backgroundColor = 'rgba(0,0,0,0.5)';

      // Osiguraj da modal-dialog bude pravilno pozicioniran
      const dialog = modal.querySelector('.modal-dialog');
      if (dialog) {
        dialog.style.position = 'relative';
        dialog.style.zIndex = '10000';
        dialog.style.margin = '1.75rem auto';
        dialog.style.pointerEvents = 'auto';
      }
    });

    // Osiguraj da modalni backdrop ima odgovarajući z-index
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
      backdrop.style.position = 'fixed';
      backdrop.style.zIndex = '9998';
      backdrop.style.backgroundColor = 'rgba(0,0,0,0.5)';
      backdrop.style.pointerEvents = 'auto';
    });
  }, 0);
}

// Pojednostavljena funkcija za pravilno prikazivanje modala
function fixModalPosition(modalElement) {
  neutralizeBodyForModal();
  const modalId = modalElement ? modalElement.id || 'unnamed-modal' : 'undefined';
  console.log('ULTRA-RADIKALNA implementacija modalnog prozora:', modalId);
  
  // 1. Provera da li je modal element uopšte prosleđen
  if (!modalElement) {
    console.warn('fixModalPosition: Modal element nije prosleđen');
    return false;
  }
  
  // 2. Provera da li je modal još uvek u DOM-u
  if (!document.body.contains(modalElement)) {
    console.error(`fixModalPosition: Modal #${modalId} nije pronađen u DOM-u!`);
    return false;
  }

  try {
    // 1. Onemogući sve postojeće Bootstrap modal instance i njihove događaje
    if ($.fn && $.fn.modal) {
      try {
        $(modalElement).modal('dispose');
      } catch (e) {
        console.log('Ne mogu dispose modal, verovatno nije inicijalizovan:', e);
      }
    }
    
    // 2. Ukloni sve postojeće modal backdrops
    $('.modal-backdrop').remove();
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
    document.querySelectorAll('[id^="portal-modal-container-"]').forEach(el => el.remove());
    document.querySelectorAll('[id^="portal-modal-backdrop-"]').forEach(el => el.remove());
    
    // 3. EKSTREMNO AGRESIVAN PRISTUP ZA REŠAVANJE PROBLEMA SA Z-INDEKSIMA
    
    // 3.1. Sačuvaj stanje skrolovanja pre otvaranja modala
    const scrollY = window.scrollY || document.documentElement.scrollTop;
    document.body.style.top = `-${scrollY}px`;
    document.body.classList.add('modal-open');
    
    // 3.2. Generiši jedinstvene ID-jeve za naše elemente
    const portalId = 'portal-modal-container-' + (Math.random().toString(36).substring(2, 10));
    const backdropId = 'portal-modal-backdrop-' + (Math.random().toString(36).substring(2, 10));
    
    // 3.3. Neutrališi sve postojeće stilove na body elementu i drugim važnim elementima
    const originalStyles = {};
    ['position', 'zIndex', 'overflow', 'pointerEvents'].forEach(prop => {
      originalStyles[prop] = document.body.style[prop];
    });
    
    // 3.4. Potpuno onemogući interakciju sa elementima ispod modala
    document.body.style.cssText += 'pointer-events: none !important; position: relative !important; z-index: auto !important;';
    
    // 3.5. Neutrališi sve problematične elemente koji bi mogli imati visok z-index
    document.querySelectorAll('.wrapper, .main-header, .main-sidebar, .content-wrapper, nav, header, aside').forEach(el => {
      if (el) {
        el.style.cssText += 'position: static !important; z-index: auto !important;';
      }
    });
    
    // 3.6. Sakrij originalni modal da se ne bi duplirao
    modalElement.style.display = 'none';
    
    // 4. KREIRAJ POTPUNO NOVI PORTAL KONTEJNER
    // Ovaj kontejner ima NAJVIŠI MOGUĆI Z-INDEX
    const portalContainer = document.createElement('div');
    portalContainer.id = portalId;
    portalContainer.setAttribute('data-original-styles', JSON.stringify(originalStyles));
    portalContainer.setAttribute('data-scroll-position', scrollY);
    
    // 4.1. Postavi ekstremno agresivne stilove za portal kontejner
    // Koristimo sve moguće tehnike da osiguramo da će se modal prikazati iznad svega
    portalContainer.style.cssText = `
      all: initial !important; /* Reset svih stilova */
      position: fixed !important;
      inset: 0 !important; /* shorthand za top, right, bottom, left */
      width: 100vw !important;
      height: 100vh !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      z-index: 2147483647 !important; /* Apsolutno najveći mogući z-index */
      pointer-events: auto !important;
      isolation: isolate !important; /* Kreira novi stacking context */
      transform: translateZ(999999px) !important; /* Kreira novi stacking context */
      will-change: transform !important; /* Poboljšava rendering u GPU */
      visibility: visible !important;
      opacity: 1 !important;
      contain: layout style paint !important; /* Performance optimizacija */
    `;
    
    // Uklonimo sve događaje koji bi mogli prekrivati modal
    document.querySelectorAll('*:not(.modal-dialog):not(.modal-content):not(.modal-body):not(.modal-header):not(.modal-footer)').forEach(el => {
      if (el !== portalContainer && !portalContainer.contains(el) && el !== modalElement) {
        el.style.pointerEvents = 'none';
      }
    });
    
    // 5. KREIRAJ BACKDROP
    const backdropElement = document.createElement('div');
    backdropElement.id = backdropId;
    backdropElement.style.cssText = `
      position: absolute !important;
      inset: 0 !important;
      width: 100% !important;
      height: 100% !important;
      background-color: rgba(0, 0, 0, 0.5) !important;
      pointer-events: auto !important;
      z-index: 0 !important;
    `;
    portalContainer.appendChild(backdropElement);
    
    // 6. KLONIRAJ SADRŽAJ MODALA U NAŠ PORTAL
    const dialogElement = modalElement.querySelector('.modal-dialog');
    if (!dialogElement) {
      console.error('Modal dialog element nije pronađen');
      return false;
    }
    
    // 6.1. Kloniraj i stilizuj modal dialog
    const newDialog = dialogElement.cloneNode(true);
    newDialog.style.cssText = `
      position: relative !important;
      margin: 1.75rem auto !important;
      pointer-events: auto !important;
      width: auto !important;
      max-width: 700px !important;
      z-index: 1 !important;
      box-shadow: 0 0 20px rgba(0,0,0,0.3) !important;
    `;
    
    // 6.2. Osiguraj da modal-content ima ispravne stilove
    const modalContent = newDialog.querySelector('.modal-content');
    if (modalContent) {
      modalContent.style.cssText += `
        background-color: white !important;
        border-radius: 4px !important;
        box-shadow: 0 0 10px rgba(0,0,0,0.2) !important;
      `;
    }
    
    // 6.3. Dodaj dijalog u portal kontejner
    portalContainer.appendChild(newDialog);
    
    // 7. DODAJ PORTAL NA KRAJ BODY-JA
    document.body.appendChild(portalContainer);
    
    // 8. POSTAVLJANJE EVENTOVA ZA ZATVARANJE
    
    // Funkcija za zatvaranje modala i čišćenje
    const closeModal = function() {
      // Pozovi našu safeHideModal funkciju
      safeHideModal(modalElement);
    };
    
    // 8.1. Zatvaranje klikom na X dugme
    const closeButtons = newDialog.querySelectorAll('[data-dismiss="modal"], .close, .btn-close');
    closeButtons.forEach(button => {
      button.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        closeModal();
      });
    });
    
    // 8.2. Zatvaranje na taster ESC
    const escHandler = function(e) {
      if (e.key === 'Escape') {
        closeModal();
        document.removeEventListener('keydown', escHandler);
      }
    };
    document.addEventListener('keydown', escHandler);
    
    // 8.3. Zatvaranje klikom na backdrop
    backdropElement.addEventListener('click', closeModal);
    
    // 8.4. Sprečavanje propagacije klika na modal dialog
    newDialog.addEventListener('click', function(e) {
      e.stopPropagation();
    });
    
    console.log('Modal uspešno prikazan u portalu sa maksimalnim z-indeksom');
    return true;
  } catch (error) {
    console.error('fixModalPosition: Greška prilikom prikazivanja modala:', error);
    return false;
  }
}

// Funkcija za kreiranje našeg backdrop-a koji će biti ispravno pozicioniran
function createCustomBackdrop(modalElement) {
  console.log('createCustomBackdrop now delegates to fixModalPosition');
  // Ova funkcija sada samo prosleđuje poziv na fixModalPosition
  fixModalPosition(modalElement);
}

// Dodajemo direktan handler za sve događaje u kalendaru
$(document).on('click', '.fc-event', function(e) {
  const eventTitle = $(this).find('.fc-event-title').text() || '';
  console.log('Direktno detektovan klik na događaj sa naslovom:', eventTitle);
  
  // Specifična provera za problematični događaj
  if (eventTitle.includes('Prva nadzorna provera') || eventTitle.includes('Dan audita')) {
    console.log('PRONAĐEN DOGAĐAJ: Prva nadzorna provera / Dan audita');
    e.preventDefault();
    e.stopPropagation();
    openAuditDayModalDirectly();
    return false;
  }
});

// Inicijalizacija modalnih dijaloga kada je dokument spreman
// Dodavanje globalnih CSS stilova za override problematičnih modal stilova
(function addGlobalModalStyles() {
  const styleElement = document.createElement('style');
  styleElement.id = 'modal-override-styles';
  styleElement.textContent = `
    /* Kreiraj vlastiti backdrop umesto Bootstrap-ovog */
    body.modal-open::after { 
      content: '' !important;
      position: fixed !important; 
      top: 0 !important;
      left: 0 !important;
      width: 100vw !important;
      height: 100vh !important;
      background-color: rgba(0, 0, 0, 0.5) !important; 
      z-index: 1950 !important;
    }
    
    /* Sakrij Bootstrap backdrop elemente potpuno */
    .modal-backdrop { 
      display: none !important; 
      opacity: 0 !important; 
      z-index: -1 !important;
      pointer-events: none !important;
    }
    
    /* Potpuno fiksiranje body elementa kada je modal otvoren */
    body.modal-open {
      overflow: hidden !important;
      position: fixed !important;
      width: 100% !important;
      height: 100% !important;
      padding-right: 0 !important; /* Uklanjamo padding jer može uzrokovati probleme */
    }
    
    /* Sprečavanje scrollovanja celog dokumenta */
    html.modal-open-html {
      overflow: hidden !important;
    }
    
    /* Osiguranje da modal ima značajno veći z-index od svih elemenata na stranici */
    .modal {
      z-index: 2000 !important;
      display: block !important;
      position: fixed !important;
      top: 0 !important;
      right: 0 !important;
      bottom: 0 !important;
      left: 0 !important;
      overflow-x: hidden !important;
      overflow-y: auto !important;
      outline: 0 !important;
    }
    
    /* Ispravna pozicija i stil za modal-dialog */
    .modal-dialog {
      margin: 1.75rem auto !important;
      position: relative !important;
      width: auto !important;
      max-width: 500px !important;
      transform: translate(0, 0) !important;
      top: 10% !important;
    }
    
    /* Ispravna pozicija za modal-content */
    .modal-content {
      position: relative !important;
      display: flex !important;
      flex-direction: column !important;
      width: 100% !important;
      background-color: #fff !important;
      border-radius: 0.3rem !important;
      box-shadow: 0 0.25rem 0.5rem rgba(0, 0, 0, 0.5) !important;
      outline: 0 !important;
    }
    
    /* Backdrop stil */
    .modal-backdrop {
      z-index: 1050 !important;
    }
    
    /* Sakrivanje modala koji nisu aktivni */
    .modal:not(.show) {
      display: none !important;
    }
  `;
  
  document.head.appendChild(styleElement);
  console.log('Dodani globalni CSS stilovi za override modal problema');
  
  // MutationObserver za praćenje i automatsko uklanjanje backdrop elemenata
  function setupMutationObserver() {
    console.log('Postavljanje MutationObserver-a za praćenje DOM promena...');
    
    // Funkcija za uklanjanje problematičnih elemenata
    const removeProblematicElements = () => {
      // 1. Ukloni sve backdrop elemente koje nisu vezani za modalni prozor
      document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
        // Proveri da li ima povezani modal koji je vidljiv
        const prevElement = backdrop.previousElementSibling;
        const isAssociatedWithVisibleModal = prevElement && 
                                           prevElement.classList.contains('modal') && 
                                           prevElement.classList.contains('show');
                                           
        if (!isAssociatedWithVisibleModal) {
          console.log('Uklanjanje backdrop elementa koji nije povezan sa vidljivim modalom');
          backdrop.style.display = 'none';
          backdrop.style.opacity = '0';
          backdrop.remove();
        }
      });
      
      // 2. Proveri da li je body u konzistentnom stanju
      const visibleModals = document.querySelectorAll('.modal.show');
      if (visibleModals.length === 0 && document.body.classList.contains('modal-open')) {
        console.log('Uklanjanje modal-open klase sa body elementa');
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('padding-right');
        document.body.style.removeProperty('overflow');
      }
    };
    
    // Debounce funkcija za efikasnije izvršavanje
    let debounceTimer;
    const debouncedRemove = () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(removeProblematicElements, 10);
    };
    
    // Kreiraj i konfiguriši observer
    const observer = new MutationObserver((mutations) => {
      let shouldRemove = false;
      
      for (let mutation of mutations) {
        // Proveri da li je dodata nova .modal-backdrop
        if (mutation.type === 'childList' && mutation.addedNodes.length) {
          for (let node of mutation.addedNodes) {
            if (node.nodeType === Node.ELEMENT_NODE) {
              if (node.classList && node.classList.contains('modal-backdrop')) {
                console.log('Detektovan novi backdrop element:', node);
                shouldRemove = true;
              }
              
              // Takođe proveri i potomke
              const backdropElements = node.querySelectorAll?.('.modal-backdrop');
              if (backdropElements && backdropElements.length > 0) {
                console.log('Detektovani backdrop elementi unutar novog čvora:', backdropElements.length);
                shouldRemove = true;
              }
            }
          }
        }
        
        // Proveri za izmene klase (npr. dodavanje 'show' klase)
        if (mutation.type === 'attributes' && 
            mutation.attributeName === 'class' && 
            mutation.target.classList && 
            mutation.target.classList.contains('modal-backdrop')) {
          console.log('Detektovana promena klase na backdrop elementu');
          shouldRemove = true;
        }
      }
      
      if (shouldRemove) {
        debouncedRemove();
      }
    });
    
    // Počni pratiti promene u DOM-u
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class']
    });
    
    console.log('MutationObserver uspešno postavljen');
    return observer;
  }
  
  // Odmah postavi observer
  const observer = setupMutationObserver();
  
  // Izvrši inicijalno čišćenje
  setTimeout(() => {
    console.log('Inicijalno čišćenje backdrop elemenata...');
    cleanupModalBackdrops(true);
  }, 500);
})();

$(document).ready(function() {
  console.log('jQuery document.ready - inicijalizacija modalnih dijaloga...');
  // Kalendar se inicijalizuje direktno u HTML šablonu
  initializeModals();
  
  // Dodatno čišćenje kada je stranica učitana
  setTimeout(function() {
    cleanupModalBackdrops(true);
  }, 1000);
});

// Funkcija za inicijalizaciju modalnih dijaloga
function initializeModals() {
  console.log('Inicijalizacija modalnih dijaloga...');
  
  // Čišćenje body stila pre inicijalizacije
  document.body.classList.remove('modal-open');
  document.body.style.removeProperty('padding-right');
  document.body.style.removeProperty('overflow');
  document.body.style.height = 'auto';
  
  // Temeljito čišćenje backdrop elemenata
  cleanupModalBackdrops(true);
  
  // Dodaj globalni event listener za ESC taster - alternativni način zatvaranja modala
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' || e.keyCode === 27) {
      const visibleModal = document.querySelector('.modal.show');
      if (visibleModal) {
        console.log('Zatvaranje modala ESC tasterom:', visibleModal.id);
        // Prvo pokušaj Bootstrap način zatvaranja
        const modalId = '#' + visibleModal.id;
        try {
          if (window.bootstrap && typeof bootstrap.Modal === 'function') {
            const bsModal = bootstrap.Modal.getInstance(visibleModal);
            if (bsModal) bsModal.hide();
          } else if (window.jQuery) {
            $(modalId).modal('hide');
          }
        } catch (e) {
          // Fallback - sakrij modal i ukloni backdrop ručno
          visibleModal.style.display = 'none';
          visibleModal.classList.remove('show');
          cleanupModalBackdrops();
        }
      }
    }
  });
  
  // Provera verzije Bootstrap-a
  const isBootstrap5 = window.bootstrap && typeof bootstrap.Modal === 'function';
  const isBootstrap4 = window.jQuery && typeof $.fn.modal === 'function';
  
  // Lista ID-eva modala koje želimo inicijalizovati
  const modalIds = ['appointmentModal', 'appointmentDetailModal', 'auditDetailModal', 
                   'auditDayModal', 'cycleAuditModal', 'dateChangeConfirmationModal'];
                   
  console.log('Detekovana verzija Bootstrap-a:', isBootstrap5 ? 'Bootstrap 5' : isBootstrap4 ? 'Bootstrap 4' : 'Nepoznata');
  
  // Inicijalizacija modala za Bootstrap 5
  if (isBootstrap5) {
    modalIds.forEach(modalId => {
      const modalElement = document.getElementById(modalId);
      if (modalElement) {
        console.log(`Inicijalizacija Bootstrap 5 modala: ${modalId}`);
        try {
          // Postavljanje opcija za modal
          const modalOptions = {
            backdrop: 'static',
            keyboard: true,
            focus: true
          };
          
          // Kreiraj novu instancu modala
          new bootstrap.Modal(modalElement, modalOptions);
          
          // Osiguranje da je modal inicijalno sakriven
          modalElement.classList.remove('show');
          modalElement.style.display = 'none';
          modalElement.setAttribute('aria-hidden', 'true');
        } catch (error) {
          console.error(`Greška pri inicijalizaciji modala ${modalId}:`, error);
        }
      } else {
        console.warn(`Modal #${modalId} nije pronađen u DOM-u!`);
      }
    });
  }
  // Inicijalizacija modala za Bootstrap 4 koristeći jQuery
  else if (isBootstrap4) {
    modalIds.forEach(modalId => {
      const $modal = $(`#${modalId}`);
      if ($modal.length > 0) {
        console.log(`Inicijalizacija Bootstrap 4 modala: ${modalId}`);
        try {
          $modal.modal({
            show: false,
            backdrop: 'static',
            keyboard: true
          });
        } catch (error) {
          console.error(`Greška pri inicijalizaciji modala ${modalId}:`, error);
        }
      } else {
        console.warn(`Modal #${modalId} nije pronađen u DOM-u!`);
      }
    });
  } 
  // Fallback ako nije dostupan ni Bootstrap 4 ni 5
  else {
    console.warn('Bootstrap nije dostupan! Pokušavam učitati Bootstrap 5.');
    // Pokušaj učitavanja Bootstrap 5 JS-a
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js';
    script.integrity = 'sha384-geWF76RCwLtnZ8qwWowPQNguL3RmwHVBC9FhGdlKrxdiJJigb/j/68SIy3Te4Bkz';
    script.crossOrigin = 'anonymous';
    document.head.appendChild(script);
    script.onload = function() {
      console.log('Bootstrap 5 JS uspešno učitan!');
      // Ponovo inicijalizuj modalne dijaloge
      setTimeout(initializeModals, 500);
    };
  }
  
  // Modernizuj Bootstrap modalne kontrole nakon inicijalizacije
  modernizeBootstrapModals();
  // Test otvaranja modala direktno iz JavaScript-a
  window.testOpenModal = function(modalId) {
    console.log('Test otvaranja modala:', modalId);
    safeShowModal('#' + modalId);
  };
  
  // Dodaj event listenere za klik na događaje u kalendaru
  setupCalendarEventHandlers();
  
  // Dodatno čišćenje backdrop elemenata kroz interval
  setInterval(function() {
    const backdropElements = document.querySelectorAll('.modal-backdrop');
    if (backdropElements.length > 0) {
      console.log(`Periodično čišćenje ${backdropElements.length} backdrop elemenata...`);
      cleanupModalBackdrops();
    }
  }, 5000); // Proveri svakih 5 sekundi
  
  // Dodaj event listener za zatvaranje modala pri kliku na backdrop
  document.addEventListener('click', function(e) {
    // Ako je kliknuto na element sa klasom modal-backdrop
    if (e.target && e.target.classList && e.target.classList.contains('modal-backdrop')) {
      console.log('Kliknuto na backdrop, zatvaranje svih modala...');
      const visibleModals = document.querySelectorAll('.modal.show');
      visibleModals.forEach(modal => {
        try {
          if (window.bootstrap && typeof bootstrap.Modal === 'function') {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();
          } else if (window.jQuery) {
            $(modal).modal('hide');
          }
        } catch (e) {
          console.warn('Greška pri zatvaranju modala:', e);
        }
      });
      cleanupModalBackdrops(true);
    }
  });
}

// Funkcija initializeCalendar je uklonjena jer se kalendar inicijalizuje direktno u HTML šablonu

/**
 * Funkcija za ispravno pozicioniranje modalnih prozora
 * Rešava problem sa modalima koji se otvaraju u donjem delu prozora
 */
function fixModalPosition(modalElement) {
  if (!modalElement) return;
  
  console.log('Popravljam poziciju modala:', modalElement.id);
  
  // Osiguraj da su stilovi za modal-dialog ispravni
  const modalDialog = modalElement.querySelector('.modal-dialog');
  if (modalDialog) {
    // Resetuj sve pozicije
    modalDialog.style.margin = '1.75rem auto';
    modalDialog.style.transform = 'none';
    
    // Resetuj top svojstvo ako je postavljeno
    if (modalDialog.style.top) {
      modalDialog.style.top = '';
    }
    
    // Resetuj pozicioniranje
    modalDialog.style.position = '';
    
    // Popravi visinu i overflow
    if (modalElement.style.height) {
      modalElement.style.height = 'auto';
    }
    
    // Osiguraj da modal ima ispravne stilove za prikazivanje
    modalElement.style.display = 'block';
    modalElement.style.paddingRight = '17px'; // Standardna vrednost za Bootstrap
    
    // Proveri da li je potrebna klasa za centriranje
    if (!modalDialog.classList.contains('modal-dialog-centered')) {
      // Dodaj samo ako nije prisutna
      modalDialog.classList.add('modal-dialog-centered');
    }
  }
  
  // Osiguraj da je body ispravno podešen
  document.body.classList.add('modal-open');
  
  // Popravi pozicioniranje modalnog prozora nakon kratke pauze
  setTimeout(() => {
    if (modalDialog && modalElement.classList.contains('show')) {
      // Proveri poziciju modala i popravi je ako je potrebno
      const rect = modalDialog.getBoundingClientRect();
      if (rect.top > window.innerHeight / 2) {
        console.log('Modal je pozicioniran prenisko, popravljam...');
        modalDialog.style.marginTop = '10vh';
      }
    }
  }, 50);
}

/**
 * Funkcija za postavljanje event handlera za kalendarske događaje
 * Osigurava da se modalima pravilno pristupa kada se klikne na događaj u kalendaru
 */
function setupCalendarEventHandlers() {
  console.log('Postavljanje handlera za kalendarske događaje...');
  
  // 1. Opšti handler za sve kalendarske događaje
  $(document).on('click', '.fc-event', function(e) {
    // Sprečavanje podrazumevanog ponašanja
    e.preventDefault();
    
    const eventElement = e.currentTarget;
    console.log('Kliknuto na događaj u kalendaru:', eventElement);
    
    // Ispitaj da li je event element div ili <a> link
    const eventId = eventElement.getAttribute('data-event-id') || 
                   $(eventElement).data('event-id') || 
                   ($(eventElement).data('fc-event') ? $(eventElement).data('fc-event').id : null);
    
    console.log('Dobijen ID događaja:', eventId);
    
    // Pokušaj prepoznati tip događaja (sastanak ili revizija/audit)
    if ($(eventElement).hasClass('appointment-event') || 
        eventElement.classList.contains('appointment-event') ||
        (eventId && eventId.toString().startsWith('appointment-'))) {
      console.log('Otvaram detalje sastanka...');
      openAppointmentModal(eventId);
    } 
    else if ($(eventElement).hasClass('audit-event') || 
            eventElement.classList.contains('audit-event') ||
            (eventId && eventId.toString().startsWith('audit-'))) {
      console.log('Otvaram detalje audita/revizije...');
      openAuditDetailModal(eventId);
    }
    else {
      // Pokušaj otvoriti generički modal za detalje
      console.log('Nepoznat tip događaja, pokušavam generički pristup...');
      
      // Pokušaj dobiti naslov i opis događaja
      const eventTitle = $(eventElement).find('.fc-title').text() || 
                        $(eventElement).find('.fc-event-title').text() || 
                        'Događaj';
      const eventDesc = $(eventElement).find('.fc-desc').text() || '';
      
      // Prvo pokušaj naći odgovarajući modal za ovaj događaj
      if (eventTitle.toLowerCase().includes('audit') || eventTitle.toLowerCase().includes('revizija')) {
        // Kreiraj objekat događaja sa minimalnim potrebnim podacima
        const eventObj = {
          title: eventTitle,
          extendedProps: {
            // Dodaj potrebne informacije koje funkcija očekuje
            appointment_id: eventId,
            description: eventDesc
          },
          start: new Date(), // Trenutno vreme kao placeholder
          end: new Date()
        };
        openAuditDetailModal(eventObj);
      } else {
        // Kreiraj objekat događaja sa minimalnim potrebnim podacima
        const eventObj = {
          title: eventTitle,
          extendedProps: {
            // Dodaj potrebne informacije koje funkcija očekuje
            appointment_id: eventId,
            description: eventDesc
          },
          start: new Date(), // Trenutno vreme kao placeholder
          end: new Date()
        };
        openAppointmentModal(eventObj);
      }
    }
  });
  
  console.log('Handleri za kalendarske događaje postavljeni.');
}
// Ovo eliminiše duplu inicijalizaciju i konflikte koji su uzrokovali probleme

// Event handleri za klik na događaje se takođe definišu direktno u HTML šablonu
// Event handleri za drag-and-drop se sada takođe definišu u HTML šablonu
// Funkcije za rad sa kalendar događajima su i dalje dostupne u JS fajlu

// Funkcija za ažuriranje datuma događaja nakon drag-and-drop operacije
function updateEventDate(eventType, eventId, newDate) {
  console.log('Ažuriranje datuma za događaj:', { eventType, eventId, newDate });
  
  // Formatiranje datuma za backend
  const isoDateTime = (newDate instanceof Date) ? newDate.toISOString() : new Date(newDate).toISOString();
  
  // Određivanje URL-a za ažuriranje u zavisnosti od tipa događaja
  const updateUrl = '/company/api/events/update-date/';
  const payload = {
    eventId: eventId,
    eventType: eventType,
    newDate: isoDateTime
  };

  if (!['audit_day', 'cycle_audit', 'appointment'].includes(eventType)) {
    console.error('Nepoznat tip događaja za ažuriranje:', eventType);
    alert('Greška: Nepoznat tip događaja za ažuriranje. Osvježite stranicu i pokušajte ponovo.');
    return;
  }
  
  // Dodavanje CSRF tokena za Django
  const csrftoken = getCookie('csrftoken');
  
  // AJAX poziv za ažuriranje datuma
  $.ajax({
    url: updateUrl,
    type: 'POST',
    data: JSON.stringify(payload),
    contentType: 'application/json',
    headers: { 'X-CSRFToken': csrftoken },
    dataType: 'json',
    success: function(response) {
      console.log('Datum uspešno ažuriran:', response);
      
      // Prikazivanje poruke o uspehu
      if (typeof Swal !== 'undefined') {
        Swal.fire({
          title: 'Uspeh!',
          text: 'Datum je uspešno ažuriran.',
          icon: 'success',
          confirmButtonText: 'U redu'
        });
      } else {
        alert('Datum je uspešno ažuriran.');
      }
      
      // Osvježavanje kalendara nakon uspešne promene
      setTimeout(function() {
        if (typeof calendar !== 'undefined') {
          calendar.refetchEvents();
        } else {
          location.reload(); // Ako calendar objekat nije dostupan
        }
      }, 1000);
    },
    error: function(xhr, status, error) {
      console.error('Greška pri ažuriranju datuma:', error);
      console.error('Status:', status);
      console.error('Response text:', xhr.responseText);
      
      let errorMsg = 'Greška prilikom ažuriranja datuma.';
      
      try {
        const response = JSON.parse(xhr.responseText);
        if (response && response.error) {
          errorMsg = response.error;
        }
      } catch (e) {
        console.error('Greška prilikom parsiranja odgovora:', e);
      }
      
      // Prikazivanje poruke o grešci
      if (typeof Swal !== 'undefined') {
        Swal.fire({
          title: 'Greška!',
          text: errorMsg,
          icon: 'error',
          confirmButtonText: 'U redu'
        });
      } else {
        alert('Greška: ' + errorMsg);
      }

      // Pokušaj da vratiš kalendar u prethodno stanje osvežavanjem događaja
      if (typeof refreshCalendar === 'function') {
        refreshCalendar();
      } else {
        try { location.reload(); } catch (e) {}
      }
    }
  });
}

// Pomoćna funkcija za formatiranje datuma za backend (YYYY-MM-DD format)
function formatDateForBackend(date) {
  if (typeof date === 'string') {
    date = new Date(date);
  }
  
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
}

// Funkcija za prikazivanje modala za potvrdu promene datuma
function showDateChangeConfirmationModal(event, newDate, callback) {
  // Formatiranje datuma za prikaz
  const formattedDate = newDate.toLocaleDateString('sr-RS', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
  
  // Priprema teksta za modal u zavisnosti od tipa događaja
  const eventType = (event.extendedProps && (event.extendedProps.eventType || event.extendedProps.type)) || null;
  let title, message, eventTitle;
  
  // Dobijanje naslova događaja za prikaz u modalu
  eventTitle = event.title || 'Događaj';
  
  if (eventType === 'audit_day') {
    title = 'Promena datuma audit dana';
    message = `Da li ste sigurni da želite da promenite datum audit dana na ${formattedDate}?`;
  } else if (eventType === 'cycle_audit') {
    title = 'Promena planiranog datuma audita';
    message = `Da li ste sigurni da želite da promenite datum audita na ${formattedDate}?`;
  } else if (eventType === 'appointment') {
    title = 'Promena datuma sastanka';
    message = `Da li ste sigurni da želite da promenite datum sastanka "${eventTitle}" na ${formattedDate}?`;
  } else {
    title = 'Promena datuma događaja';
    message = `Da li ste sigurni da želite da promenite datum događaja na ${formattedDate}?`;
  }
  
  // Koristi SweetAlert2 za lepši i moderniji prikaz modala
  if (typeof Swal !== 'undefined') {
    // Koristi SweetAlert2 ako je dostupan
    Swal.fire({
      title: title,
      html: message,
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Potvrdi',
      cancelButtonText: 'Otkaži',
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      focusCancel: true
    }).then((result) => {
      if (result.isConfirmed) {
        if (typeof callback === 'function') {
          callback(true);
        }
      } else {
        if (typeof callback === 'function') {
          callback(false);
        }
      }
    });
  } else {
    // Fallback na Bootstrap modal ako SweetAlert2 nije dostupan
    // Proveri da li modal već postoji, ako ne, kreiraj ga
    let $modal = $('#dateChangeConfirmationModal');
    if ($modal.length === 0) {
      // Kreiraj modal ako ne postoji - Bootstrap 5 verzija
      // Prvo ukloni sve postojeće instance ovog modala da ne bismo imali duplikate
      $('#dateChangeConfirmationModal').remove();
      
      // Zatim dodaj novi modal na kraj body elementa
      $('body').append(`
        <div class="modal fade" id="dateChangeConfirmationModal" tabindex="-1" aria-labelledby="dateChangeConfirmationModalLabel" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="dateChangeConfirmationModalLabel">Promena datuma</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body">
                <p id="dateChangeConfirmationMessage"></p>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" id="dateChangeCancel" data-bs-dismiss="modal">Otkaži</button>
                <button type="button" class="btn btn-primary" id="dateChangeConfirm">Potvrdi</button>
              </div>
            </div>
          </div>
        </div>
      `);
      
      // Osiguramo da je modal zaista dodan u DOM i spreman za upotrebu
      console.log('Dinamički kreiran modal #dateChangeConfirmationModal je dodan u DOM');
      
      // Pauza da osiguramo da je DOM ažuriran
      setTimeout(() => {
        $modal = $('#dateChangeConfirmationModal');
        // Nastavi sa ostatkom koda za modal
        continueWithModal();
      }, 50); // mali delay da osiguramo da je DOM ažuriran
      return; // Prekini izvršavanje i pusti setTimeout da nastavi
    }
    
    // Ako je modal već postojao u DOM-u, nastavi odmah
    continueWithModal();
    
    // Funkcija koja nastavlja sa postavljanjem poruka i prikazom modala
    function continueWithModal() {
    
    // Postavi naslov i poruku
    $modal.find('.modal-title').text(title);
    $modal.find('#dateChangeConfirmationMessage').text(message);
    
    // Postavi handlere za dugmad koristeći Bootstrap 5 API
    $modal.find('#dateChangeConfirm').off('click').on('click', function() {
      try {
        const modalElement = document.getElementById('dateChangeConfirmationModal');
        const dateChangeModal = bootstrap.Modal.getInstance(modalElement);
        if (dateChangeModal) {
          dateChangeModal.hide();
        } else {
          // Fallback na direktnu DOM manipulaciju
          modalElement.classList.remove('show');
          modalElement.style.display = 'none';
          document.body.classList.remove('modal-open');
        }
      } catch (error) {
        console.error('Greška pri zatvaranju modala:', error);
      }
      
      if (typeof callback === 'function') {
        callback(true);
      }
    });
    
    $modal.find('#dateChangeCancel').off('click').on('click', function() {
      try {
        const modalElement = document.getElementById('dateChangeConfirmationModal');
        const dateChangeModal = bootstrap.Modal.getInstance(modalElement);
        if (dateChangeModal) {
          dateChangeModal.hide();
        } else {
          // Fallback na direktnu DOM manipulaciju
          modalElement.classList.remove('show');
          modalElement.style.display = 'none';
          document.body.classList.remove('modal-open');
        }
      } catch (error) {
        console.error('Greška pri zatvaranju modala:', error);
      }
      
      if (typeof callback === 'function') {
        callback(false);
      }
    });
    
    // Prikaži modal koristeći našu unapređenu metodu
    try {
      const modalElement = document.getElementById('dateChangeConfirmationModal');
      if (!modalElement) {
        throw new Error('Modal element nije pronađen u DOM-u');
      }
      
      // Pokušaj prikazati modal koristeći našu robusnu fixModalPosition funkciju
      if (typeof fixModalPosition === 'function') {
        console.log('Prikazujem modal koristeći fixModalPosition...');
        const success = fixModalPosition(modalElement);
        if (!success) {
          throw new Error('fixModalPosition nije uspeo prikazati modal');
        }
      } else {
        // Ako naša funkcija nije dostupna, koristi Bootstrap 5 API
        console.log('fixModalPosition nije dostupan, koristim Bootstrap API...');
        const dateChangeModal = new bootstrap.Modal(modalElement);
        dateChangeModal.show();
      }
    } catch (error) {
      console.error('Greška pri otvaranju modala za potvrdu promene datuma:', error);
      // Fallback na direktnu DOM manipulaciju ako sve druge metode ne uspeju
      try {
        const modalElement = document.getElementById('dateChangeConfirmationModal');
        if (modalElement) {
          modalElement.classList.add('show');
          modalElement.style.display = 'block';
          document.body.classList.add('modal-open');
        } else {
          console.error('Modal #dateChangeConfirmationModal nije pronađen u DOM-u!'); 
        }
      } catch (fallbackError) {
        console.error('Fatalna greška pri prikazivanju modala:', fallbackError);
      }
    }
  } // Kraj continueWithModal funkcije
  } // Kraj else bloka koji proverava SweetAlert
} // Kraj showDateChangeConfirmationModal funkcije

// Funkcija za obradu promene datuma događaja nakon drag-and-drop
function handleEventDateChange(info) {
  const event = info.event;
  const eventProps = event.extendedProps || {};
  const eventType = eventProps.eventType;
  
  console.log('Događaj premešten:', {
    event: event,
    eventType: eventType,
    extendedProps: eventProps
  });
  
  // Izvuci ID događaja u zavisnosti od tipa
  let eventId;
  
  if (eventType === 'audit_day') {
    eventId = eventProps.audit_day_id || event.id;
  } else if (eventType === 'cycle_audit') {
    eventId = eventProps.cycle_id || event.id;
  } else if (eventType === 'appointment') {
    eventId = event.id.replace('appointment_', '');
  } else {
    console.warn('Pomeranje ovog tipa događaja nije podržano:', eventType);
    info.revert(); // Vrati događaj na originalnu poziciju
    return;
  }
  
  const newDate = event.start;
  
  console.log('Događaj premešten - detalji:', {
    eventType: eventType,
    eventId: eventId,
    newDate: newDate
  });
  
  // Prikaži modal za potvrdu promene datuma
  showDateChangeConfirmationModal(event, newDate, function(confirmed) {
    if (confirmed) {
      // Korisnik je potvrdio promenu, ažuriraj datum na serveru
      updateEventDate(eventType, eventId, newDate);
    } else {
      // Korisnik je otkazao promenu, vrati događaj na originalnu poziciju
      info.revert();
    }
  });
}

/**
 * ISOQAR Calendar.js
 * Glavna JavaScript datoteka za kalendar funkcionalnosti
 * Uključuje podršku za drag-and-drop događaja
 */

// Funkcija za dobijanje CSRF tokena iz cookie-a
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// POTPUNO NOVA funkcija za sigurno prikazivanje modala
function safeShowModal(modalSelector) {
  neutralizeBodyForModal();
  console.log('NOVA safeShowModal funkcija pokrenuta za:', modalSelector);
  
  // 1. UKLANJAMO SVE POSTOJEĆE BACKDROPS
  document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
  
  // 2. DOBAVI MODAL ELEMENT - podrška za string, DOM element i jQuery
  let modalElement;
  if (typeof modalSelector === 'string') {
    modalElement = document.querySelector(modalSelector);
  } else if (modalSelector instanceof Element) {
    modalElement = modalSelector;
  } else if (modalSelector && typeof jQuery !== 'undefined' && modalSelector instanceof jQuery) {
    modalElement = modalSelector[0];
  }
  
  if (!modalElement) {
    console.error(`Modal nije pronađen: ${modalSelector}`);
    return false;
  }
  
  console.log('Pronađen modal element:', modalElement.id || 'unnamed-modal');
  
  // 3. ONEMOGUĆIMO BOOTSTRAP API ZA OVAJ MODAL
  if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
    try {
      const bsModal = bootstrap.Modal.getInstance(modalElement);
      if (bsModal) bsModal.dispose();
    } catch(e) { /* ignorišemo greške */ }
  }
  
  // 4. ISKLJUČIMO SVE BOOTSTRAP EVENT LISTENERE
  if (typeof $ !== 'undefined') {
    try {
      $(modalElement).off();
    } catch(e) { /* ignorišemo greške */ }
  }
  
  // 5. SPASIMO SCROLL POZICIJU
  const scrollY = window.scrollY || window.pageYOffset;
  document.body.style.top = `-${scrollY}px`;
  console.log(`Sačuvana pozicija scrollovanja: ${scrollY}px`);
  
  // 6. KORISTIMO NAŠU POTPUNO NOVU IMPLEMENTACIJU
  return fixModalPosition(modalElement);
}
  
  // Osiguranje da nema dupliranih modala pre prikaza
  removeDuplicateModals();
  
  // Fiksiranje veličine prozora pre otvaranja modala
  document.body.style.width = `${window.innerWidth}px`;
  
  // Osiguranje da su modali inicijalno sakriveni (osim onog koji treba prikazati)
  document.querySelectorAll('.modal').forEach(modal => {
    if (modal !== modalElement) {
      modal.style.display = 'none';
      modal.classList.remove('show');
      modal.setAttribute('aria-hidden', 'true');
    }
  });
  
  // Uklanjanje postojećih backdrop-ova ili prilagodba z-index vrednosti
  document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
    // Umesto uklanjanja, postavimo backdrop iza modala
    backdrop.style.zIndex = '1040'; // Vrednost ispod modala (2060)
  });
  
  // Dodatno, kreiramo novi backdrop sa definisanim z-index-om
  // koji će biti ispod modala
  const newBackdrop = document.createElement('div');
  newBackdrop.className = 'modal-backdrop fade show';
  newBackdrop.style.zIndex = '1040';
  document.body.appendChild(newBackdrop);
  
  // Uklanjanje modal-open klase sa body-ja pre ponovnog otvaranja
  document.body.classList.remove('modal-open');
  document.body.style.paddingRight = '';

/**
 * Funkcija za temeljito čišćenje svih modal backdrop elemenata
 * Agresivno uklanja sve zaostale backdrop elemente na stranici
 */
function cleanupModalBackdrops(force = false) {
  console.log('Počinjem temeljito čišćenje backdrop elemenata...');
  
  // 1. Prvo prebroji backdrop elemente
  const backdropElements = document.querySelectorAll('.modal-backdrop');
  const backdropCount = backdropElements.length;
  console.log(`Pronađeno ${backdropCount} backdrop elemenata za uklanjanje`);
  
  if (backdropCount === 0 && !force) {
    return; // Nema potrebe za čišćenjem
  }
  
  // 2. Primeni različite metode uklanjanja
  
  // Metoda 1: Standardno uklanjanje putem remove()
  backdropElements.forEach(backdrop => {
    // Prvo sakrivanje
    backdrop.style.display = 'none';
    backdrop.style.opacity = '0';
    backdrop.classList.remove('show', 'fade');
    // Zatim uklanjanje
    try {
      backdrop.remove();
    } catch (e) {
      console.warn('Greška pri uklanjanju backdrop elementa:', e);
    }
  });
  
  // Metoda 2: Uklanjanje pomoću parentNode.removeChild
  setTimeout(() => {
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
      try {
        if (backdrop.parentNode) {
          backdrop.parentNode.removeChild(backdrop);
        }
      } catch (e) {
        console.warn('Greška pri uklanjanju backdrop elementa preko parentNode:', e);
      }
    });
  }, 50);
  
  // Metoda 3: jQuery metoda ako je dostupna
  if (window.jQuery) {
    setTimeout(() => {
      try {
        $('.modal-backdrop').remove();
      } catch (e) {
        console.warn('Greška pri jQuery uklanjanju backdrop elemenata:', e);
      }
    }, 100);
  }
  
  // Metoda 4: Force override putem CSS
  const styleEl = document.createElement('style');
  styleEl.textContent = '.modal-backdrop { display: none !important; opacity: 0 !important; }'; 
  document.head.appendChild(styleEl);
  setTimeout(() => document.head.removeChild(styleEl), 500); // Ukloni nakon 500ms
  
  // Proveri nakon kratke pauze da li je uklanjanje uspelo
  setTimeout(() => {
    const remainingBackdrops = document.querySelectorAll('.modal-backdrop');
    if (remainingBackdrops.length > 0) {
      console.warn(`I dalje postoji ${remainingBackdrops.length} backdrop elemenata nakon čišćenja!`);
      // Pokušaj brutalno čišćenje putem innerHTML
      if (force) {
        Array.from(remainingBackdrops).forEach(backdrop => {
          if (backdrop.parentNode) {
            try {
              const parent = backdrop.parentNode;
              const tempHtml = parent.innerHTML;
              parent.innerHTML = tempHtml.replace(/<div class="modal-backdrop[^>]*>/g, ''); 
            } catch (e) {
              console.error('Greška pri forsiranom čišćenju backdrop elementa:', e);
            }
          }
        });
      }
    } else {
      console.log('Uspešno uklonjeni svi backdrop elementi!');
    }
  }, 200);
}

/**
 * Funkcija za bezbedno zatvaranje modalnog prozora
 * Ovo je komplementarno sa fixModalPosition funkcijom
 * Uklanja sve kreirane portale i backdrop elemente i vraća originalne stilove
 */
function safeHideModal(modalElement) {
  console.log('safeHideModal pozvan za modal:', modalElement ? modalElement.id || 'unnamed-modal' : 'undefined');

  if (!modalElement) {
    console.warn('safeHideModal: Modal element nije prosleđen');
    return false;
  }

  try {
    // 1. Uklanjanje svih portal kontejnera i vraćanje originalnih stilova
    document.querySelectorAll('[id^="portal-modal-container-"]').forEach(portal => {
      console.log('Obrađujem portal kontejner:', portal.id);
      
      // 1.1 Vrati originalne stilove ako su sačuvani kao JSON u data atributu
      try {
        const originalStylesJSON = portal.getAttribute('data-original-styles');
        if (originalStylesJSON) {
          const originalStyles = JSON.parse(originalStylesJSON);
          for (const [prop, value] of Object.entries(originalStyles)) {
            if (prop && value !== undefined) {
              document.body.style[prop] = value;
              console.log(`Vraćen originalni stil za ${prop}:`, value);
            }
          }
        }
      } catch (e) {
        console.warn('Greška pri vraćanju originalnih stilova:', e);
      }
      
      // 1.2 Vrati scroll poziciju ako je sačuvana
      try {
        const scrollY = parseInt(portal.getAttribute('data-scroll-position'), 10);
        if (!isNaN(scrollY)) {
          document.body.style.top = '';
          window.scrollTo(0, Math.abs(scrollY));
          console.log(`Vraćena pozicija scrollovanja: ${Math.abs(scrollY)}px`);
        }
      } catch (e) {
        console.warn('Greška pri vraćanju scrollY pozicije:', e);
      }
      
      // 1.3 Ukloni portal kontejner
      console.log('Uklanjam portal kontejner:', portal.id);
      portal.remove();
    });

    // 2. Uklanjanje svih backdrop elemenata
    document.querySelectorAll('[id^="portal-modal-backdrop-"], .modal-backdrop').forEach(backdrop => {
      console.log('Uklanjam backdrop element:', backdrop.id || backdrop.className);
      backdrop.remove();
    });

    // 3. Resetovanje stanja originalnog modalnog prozora
    modalElement.style.display = 'none';
    modalElement.classList.remove('show');
    modalElement.setAttribute('aria-hidden', 'true');

    // 4. Agresivno čišćenje i resetovanje svih stilova
    document.body.classList.remove('modal-open');
    
    // 4.1 Vrati osnovne stilove na body elementu
    document.body.style.position = '';
    document.body.style.zIndex = '';
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
    document.body.style.top = '';
    document.body.style.pointerEvents = 'auto';
    
    // 4.2 Resetuj stilove na svim potencijalno problematičnim elementima
    document.querySelectorAll('.wrapper, .main-header, .main-sidebar, .content-wrapper, nav, header, aside').forEach(el => {
      if (el) {
        el.style.position = '';
        el.style.zIndex = '';
      }
    });
    
    // 4.3 Dodatno čišćenje inline stilova koji mogu praviti probleme
    const problematicInlineStyles = [
      'position: static !important',
      'z-index: auto !important',
      'pointer-events: none !important'
    ];
    
    // Funkcija koja čisti problematične stilove iz style atributa
    const cleanInlineStyles = (element) => {
      if (element && element.style && element.style.cssText) {
        let cssText = element.style.cssText;
        problematicInlineStyles.forEach(style => {
          cssText = cssText.replace(style, '');
        });
        element.style.cssText = cssText.trim();
      }
    };
    
    // Primeni čišćenje na body i druge elemente
    cleanInlineStyles(document.body);
    document.querySelectorAll('.wrapper, .main-header, .main-sidebar, .content-wrapper, nav, header, aside').forEach(cleanInlineStyles);

    console.log('safeHideModal: Modal uspešno zatvoren');
    return true;
  } catch (error) {
    console.error('safeHideModal: Greška prilikom zatvaranja modala:', error);
    return false;
  }
}

// Funkcija koja proverava CSS stilove modala
function checkModalStyles(modalSelector) {
  try {
    console.log('Proveravam CSS stilove za modal:', modalSelector);
    const $modal = $(modalSelector);
    
    if ($modal.length === 0) {
      console.error('Modal nije pronađen za proveru stilova:', modalSelector);
      return;
    }
    
    // Proveri trenutne stilove
    const computedStyle = window.getComputedStyle($modal[0]);
    console.log('Modal computed styles:', {
      display: computedStyle.display,
      visibility: computedStyle.visibility,
      opacity: computedStyle.opacity,
      zIndex: computedStyle.zIndex,
      position: computedStyle.position
    });
    
    // Proveri da li postoje problemi sa stilovima
    if (computedStyle.display === 'none' && $modal.hasClass('show')) {
      console.warn('Modal ima klasu show, ali display: none');
    }
    
    if (computedStyle.visibility === 'hidden') {
      console.warn('Modal ima visibility: hidden');
    }
    
    if (computedStyle.opacity === '0') {
      console.warn('Modal ima opacity: 0');
    }
    
    if (parseInt(computedStyle.zIndex, 10) < 1000) {
      console.warn('Modal ima nizak z-index:', computedStyle.zIndex);
    }
    
    // Proveri backdrop ako postoji
    const $backdrop = $('.modal-backdrop');
    if ($backdrop.length > 0) {
      const backdropComputedStyle = window.getComputedStyle($backdrop[0]);
      console.log('Backdrop computed styles:', {
        display: backdropComputedStyle.display,
        visibility: backdropComputedStyle.visibility,
        opacity: backdropComputedStyle.opacity,
        zIndex: backdropComputedStyle.zIndex
      });
    }
  } catch (error) {
    console.error('Greška prilikom provere CSS stilova:', error);
  }
}

// Funkcija koja pokušava više metoda za otvaranje modala
function tryMultipleModalOpenMethods(modalSelector) {
  try {
    // 1. Standardni jQuery pristup
    const $modal = $(modalSelector);
    console.log('Modal element:', $modal);
    console.log('Modal element postoji:', $modal.length > 0);
    
    if ($modal.length === 0) {
      console.error('Modal nije pronađen:', modalSelector);
      return;
    }
    
    // Ukloni aria-hidden atribut da bi modal bio dostupan za čitače ekrana
    $modal.removeAttr('aria-hidden');
    
    // Proveri da li je modal već u DOM-u i vidljiv
    console.log('Modal trenutno vidljiv:', $modal.is(':visible'));
    console.log('Modal trenutne klase:', $modal.attr('class'));
    
    // Resetuj modal pre prikazivanja
    $modal.removeClass('show');
    $modal.css('display', 'none');
    
    // Prikaži modal korišćenjem direktnog jQuery poziva
    console.log('Metoda 1: Direktno prikazujem modal korišćenjem jQuery...');
    try {
      $modal.modal('show');
      console.log('jQuery Modal.show() je pozvan');
    } catch (err) {
      console.warn('Greška pri pozivanju jQuery modal("show"):', err);
    }
    
    // Postavi fokus na prvi element koji može da primi fokus u modalu
    $modal.on('shown.bs.modal', function() {
      console.log('Modal je prikazan (shown.bs.modal event)');
      const focusableElements = $modal.find('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
      if (focusableElements.length > 0) {
        focusableElements[0].focus();
      }
    });
    
    // 2. Pokušaj sa direktnim Bootstrap API-jem nakon kratke pauze
    setTimeout(function() {
      if (!$modal.hasClass('show') || !$modal.is(':visible')) {
        console.log('Metoda 2: Modal još nije prikazan, pokušavam sa Bootstrap.Modal.getInstance...');
        try {
          // Pokušaj sa Bootstrap 4 API-jem
          if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modalInstance = bootstrap.Modal.getInstance($modal[0]);
            if (modalInstance) {
              modalInstance.show();
              console.log('Bootstrap.Modal.getInstance().show() je pozvan');
            } else {
              console.log('Nije pronađena instanca modala, kreiram novu...');
              const newModalInstance = new bootstrap.Modal($modal[0]);
              newModalInstance.show();
              console.log('new Bootstrap.Modal().show() je pozvan');
            }
          } else {
            console.log('Bootstrap objekat nije dostupan, pokušavam sa jQuery metodom...');
            $modal.modal({show: true});
          }
        } catch (err) {
          console.warn('Greška pri korišćenju Bootstrap API-ja:', err);
        }
      } else {
        console.log('Modal je već prikazan nakon metode 1');
      }
    }, 100);
    
    // 3. Pokušaj sa jQuery trigger metodom nakon još malo vremena
    setTimeout(function() {
      if (!$modal.hasClass('show') || !$modal.is(':visible')) {
        console.log('Metoda 3: Modal još nije prikazan, pokušavam sa jQuery trigger...');
        try {
          $modal.trigger('show.bs.modal');
          console.log('jQuery trigger("show.bs.modal") je pozvan');
          
          // Pokušaj i sa direktnim pozivom
          $modal.modal('show');
        } catch (err) {
          console.warn('Greška pri korišćenju jQuery trigger:', err);
        }
      } else {
        console.log('Modal je već prikazan nakon metode 2');
      }
    }, 200);
    
    // 4. Pokušaj sa direktnim postavljanjem HTML atributa
    setTimeout(function() {
      if (!$modal.hasClass('show') || !$modal.is(':visible')) {
        console.log('Metoda 4: Modal još nije prikazan, pokušavam sa direktnim postavljanjem HTML atributa...');
        try {
          // Dodaj backdrop ako ne postoji
          if ($('.modal-backdrop').length === 0) {
            $('body').append('<div class="modal-backdrop fade show"></div>');
          }
          
          // Postavi CSS i klase direktno
          $modal.addClass('show');
          $modal.attr('aria-modal', 'true');
          $modal.css({
            'display': 'block',
            'z-index': '1050',
            'visibility': 'visible',
            'opacity': '1',
            'pointer-events': 'auto'
          });
          $('body').addClass('modal-open');
          
          console.log('Direktno postavljanje HTML atributa je izvršeno');
          
          // Proveri da li je modal sada vidljiv
          console.log('Modal je sada vidljiv:', $modal.is(':visible'));
        } catch (err) {
          console.warn('Greška pri direktnom postavljanju HTML atributa:', err);
        }
      } else {
        console.log('Modal je već prikazan nakon metode 3');
      }
    }, 300);
    
    // 5. Krajnji pokušaj - direktno otvaranje modala preko alert dijaloga
    setTimeout(function() {
      if (!$modal.hasClass('show') || !$modal.is(':visible')) {
        console.log('Metoda 5: Modal još nije prikazan, pokušavam sa alert dijalogom...');
        try {
          alert('Modal se ne može prikazati. Molimo osvježite stranicu i pokušajte ponovo.');
        } catch (err) {
          console.warn('Greška pri prikazivanju alert dijaloga:', err);
        }
      } else {
        console.log('Modal je već prikazan nakon metode 4');
      }
    }, 500);
  } catch (error) {
    console.error('Greška prilikom otvaranja modala:', error);
  }
}

// Funkcija za otvaranje modala za detalje audit dana
function openAuditDayModal(event) {
  console.log('Otvaranje modala za audit dan:', event);
  console.log('Event type:', event.extendedProps?.type || event.extendedProps?.eventType);
  console.log('Event title:', event.title);
  
  try {
    const auditDayId = event.extendedProps?.audit_day_id || event.extendedProps?.id || event.id;
    console.log('Audit Day ID:', auditDayId);
    
    if (!auditDayId) {
      console.error('Nije pronađen ID audit dana');
      return;
    }
    
    // Provera da li modal postoji u DOM-u
    const modalExists = $('#auditDetailModal').length > 0;
    console.log('Modal #auditDetailModal postoji u DOM-u:', modalExists);
    
    if (!modalExists) {
      console.error('Modal #auditDetailModal ne postoji u DOM-u!');
      alert('Greška: Modal za prikaz detalja audit dana nije pronađen.');
      return;
    }
    
    console.log('Popunjavam modal sa podacima...');
    $('#auditDetailModalLabel').text('Detalji audit dana');
    $('#audit-company').text(event.extendedProps?.company_name || 'Nije dostupno');
    $('#audit-type').text(event.extendedProps?.audit_type || 'Nije dostupno');
    $('#audit-status').text(event.extendedProps?.status || 'Nije dostupno');
    $('#audit-planned-date').text(event.extendedProps?.planned_date || event.start?.toLocaleDateString('sr-RS') || 'Nije dostupno');
    $('#audit-actual-date').text(event.extendedProps?.actual_date || 'Nije zakazano');
    $('#audit-days-count').text(event.extendedProps?.days_count || '1');
    $('#audit-notes').text(event.extendedProps?.notes || 'Nema napomena');
    
    console.log('Pozivam safeShowModal za #auditDetailModal...');
    safeShowModal('#auditDetailModal');
    
    // Dodatni pokušaj direktnog otvaranja modala nakon kratke pauze
    setTimeout(function() {
      console.log('Pokušavam direktno otvaranje modala preko jQuery...');
      $('#auditDetailModal').modal('show');
      console.log('Direktno otvaranje modala izvršeno.');
    }, 500);
  } catch (error) {
    console.error('Greška prilikom otvaranja audit day modala:', error);
  }
}

// Funkcija za otvaranje modala za detalje certifikacionog ciklusa
function openCycleAuditModal(event) {
  console.log('Otvaranje modala za ciklus audit:', event);
  console.log('Event type:', event.extendedProps?.type || event.extendedProps?.eventType);
  console.log('Event title:', event.title);
  
  try {
    const cycleAuditId = event.extendedProps?.cycle_audit_id || event.extendedProps?.id || event.id;
    console.log('Cycle Audit ID:', cycleAuditId);
    
    if (!cycleAuditId) {
      console.error('Nije pronađen ID ciklus audita');
      return;
    }
    
    // Provera da li modal postoji u DOM-u
    const cycleAuditModalExists = $('#cycleAuditModal').length > 0;
    console.log('Modal #cycleAuditModal postoji u DOM-u:', cycleAuditModalExists);
    
    if (!cycleAuditModalExists) {
      console.error('Modal #cycleAuditModal ne postoji u DOM-u!');
      alert('Greška: Modal za prikaz detalja certifikacionog ciklusa nije pronađen.');
      return;
    }
    
    console.log('Popunjavam modal sa podacima...');
    $('#cycleAuditModalLabel').text('Detalji certifikacionog ciklusa');
    $('#cycle-company').text(event.extendedProps?.company_name || 'Nije dostupno');
    $('#cycle-audit-type').text(event.extendedProps?.audit_type || 'Nije dostupno');
    $('#cycle-status').text(event.extendedProps?.status || 'Nije dostupno');
    $('#cycle-id').text(event.extendedProps?.cycle_id || 'Nije dostupno');
    $('#cycle-start-date').text(event.extendedProps?.cycle_start_date || 'Nije dostupno');
    $('#cycle-end-date').text(event.extendedProps?.cycle_end_date || 'Nije dostupno');
    $('#cycle-planned-date').text(event.extendedProps?.planned_date || event.start?.toLocaleDateString('sr-RS') || 'Nije dostupno');
    $('#cycle-notes').text(event.extendedProps?.notes || 'Nema napomena');
    
    console.log('Pozivam safeShowModal za #cycleAuditModal...');
    safeShowModal('#cycleAuditModal');
    
    setTimeout(function() {
      $('#cycleAuditModal').modal('show');
      console.log('Direktno otvaranje modala izvršeno.');
    }, 500);
  } catch (error) {
    console.error('Greška prilikom otvaranja modala za ciklus audit:', error);
  }
}

// Funkcija za otvaranje modala za detalje termina/sastanka
function openAppointmentModal(event) {
  console.log('Otvaranje modala za termin/sastanak:', event);
  console.log('Event type:', event.extendedProps?.type || event.extendedProps?.eventType);
  console.log('Event title:', event.title);
  
  try {
    const appointmentId = event.extendedProps?.appointment_id || event.extendedProps?.id || event.id;
    console.log('Appointment ID:', appointmentId);
    
    if (!appointmentId) {
      console.error('Nije pronađen ID termina');
      return;
    }
    
    // Provera da li modal postoji u DOM-u
    const appointmentDetailModalExists = $('#appointmentDetailModal').length > 0;
    console.log('Modal #appointmentDetailModal postoji u DOM-u:', appointmentDetailModalExists);
    
    if (!appointmentDetailModalExists) {
      console.error('Modal #appointmentDetailModal ne postoji u DOM-u!');
      alert('Greška: Modal za prikaz detalja termina nije pronađen.');
      return;
    }
    
    console.log('Popunjavam modal sa podacima...');
    $('#appointmentDetailModalLabel').text('Detalji termina');
    $('#appointment-title').text(event.title || 'Bez naslova');
    $('#appointment-company').text(event.extendedProps?.company_name || 'Nije dostupno');
    $('#appointment-type').text(event.extendedProps?.appointment_type || 'Nije dostupno');
    $('#appointment-start').text(event.start?.toLocaleString('sr-RS') || 'Nije dostupno');
    $('#appointment-end').text(event.end?.toLocaleString('sr-RS') || 'Nije dostupno');
    $('#appointment-location').text(event.extendedProps?.location || 'Nije navedeno');
    $('#appointment-is-online').text(event.extendedProps?.is_online ? 'Da' : 'Ne');
    $('#appointment-meeting-link').text(event.extendedProps?.meeting_link || 'Nije dostupno');
    $('#appointment-status').text(event.extendedProps?.status || 'Nije dostupno');
    $('#appointment-notes').text(event.extendedProps?.notes || 'Nema napomena');
    
    console.log('Pozivam safeShowModal za #appointmentDetailModal...');
    safeShowModal('#appointmentDetailModal');
    
    setTimeout(function() {
      $('#appointmentDetailModal').modal('show');
      console.log('Direktno otvaranje modala izvršeno.');
    }, 500);
  } catch (error) {
    console.error('Greška prilikom otvaranja modala za termin:', error);
  }
}

// Funkcija za prikazivanje modala za potvrdu promene datuma događaja
function showDateChangeConfirmationModal(event, newDate, callback) {
  const formattedDate = newDate.toLocaleDateString('sr-RS', { year: 'numeric', month: '2-digit', day: '2-digit' });
  const eventType = event.extendedProps?.type || event.extendedProps?.eventType;
  let title, message, eventTitle;
  
  eventTitle = event.title || 'Događaj';
  
  if (eventType === 'audit_day') {
    title = 'Promena datuma audit dana';
    message = `Da li ste sigurni da želite da promenite datum audit dana na ${formattedDate}?`;
  } else if (eventType === 'cycle_audit') {
    title = 'Promena planiranog datuma audita';
    message = `Da li ste sigurni da želite da promenite datum audita na ${formattedDate}?`;
  } else if (eventType === 'appointment') {
    title = 'Promena datuma sastanka';
    message = `Da li ste sigurni da želite da promenite datum sastanka "${eventTitle}" na ${formattedDate}?`;
  } else {
    title = 'Promena datuma događaja';
    message = `Da li ste sigurni da želite da promenite datum događaja na ${formattedDate}?`;
  }
  
  // Proveri da li je SweetAlert2 dostupan
  if (typeof Swal !== 'undefined') {
    // Koristi SweetAlert2 za lepši prikaz
    Swal.fire({
      title: title,
      text: message,
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Da, promeni datum',
      cancelButtonText: 'Otkaži'
    }).then((result) => {
      if (result.isConfirmed) {
        callback(true);
      } else {
        callback(false);
      }
    });
  } else {
    // Fallback na standardni confirm
    const confirmed = confirm(message);
    callback(confirmed);
  }
}

// Funkcija za ažuriranje datuma događaja na serveru
function updateEventDate(eventType, eventId, newDate) {
  console.log('Ažuriranje datuma događaja na serveru:', {
    eventType: eventType,
    eventId: eventId,
    newDate: (newDate instanceof Date) ? newDate.toISOString() : new Date(newDate).toISOString()
  });
  
  const csrftoken = getCookie('csrftoken');
  const payload = {
    eventType: eventType,
    eventId: eventId,
    newDate: (newDate instanceof Date) ? newDate.toISOString() : new Date(newDate).toISOString()
  };
  
  $.ajax({
    url: '/company/api/events/update-date/',
    type: 'POST',
    data: JSON.stringify(payload),
    contentType: 'application/json',
    headers: { 'X-CSRFToken': csrftoken },
    success: function(response) {
      console.log('Uspešno ažuriran datum događaja:', response);
      
      if (response.success) {
        if (typeof Swal !== 'undefined') {
          Swal.fire({
            title: 'Uspešno',
            text: 'Datum događaja je uspešno ažuriran.',
            icon: 'success',
            confirmButtonText: 'U redu'
          });
        } else {
          alert('Datum događaja je uspešno ažuriran.');
        }
        
        refreshCalendar();
      } else {
        if (typeof Swal !== 'undefined') {
          Swal.fire({
            title: 'Greška',
            text: response.error || 'Došlo je do greške prilikom ažuriranja datuma događaja.',
            icon: 'error',
            confirmButtonText: 'U redu'
          });
        } else {
          alert('Greška: ' + (response.error || 'Došlo je do greške prilikom ažuriranja datuma događaja.'));
        }
      }
    },
    error: function(xhr, status, error) {
      console.error('Greška pri ažuriranju datuma događaja:', error);
      
      // Pokušaj da pročitaš JSON odgovor sa greškama i prikažeš korisniku
      let serverMsg = null;
      try {
        const resp = xhr.responseJSON || JSON.parse(xhr.responseText || '{}');
        serverMsg = resp && (resp.error || resp.message);
      } catch (e) {
        // Ignoriši parse grešku
      }

      if (typeof Swal !== 'undefined') {
        Swal.fire({
          title: 'Greška',
          text: serverMsg || 'Došlo je do greške prilikom ažuriranja datuma događaja.',
          icon: 'error',
          confirmButtonText: 'U redu'
        });
      } else {
        alert('Greška: ' + (serverMsg || 'Došlo je do greške prilikom ažuriranja datuma događaja.'));
      }
    }
  });
}

// Funkcija za osvežavanje kalendara
function refreshCalendar() {
  try {
    // Pokušaj da dobiješ instancu kalendara
    const calendarEl = document.getElementById('calendar');
    if (calendarEl) {
      const calendarApi = calendarEl._calendar?.getApi ? calendarEl._calendar.getApi() : null;
      
      if (calendarApi) {
        console.log('Osvežavanje kalendara...');
        calendarApi.refetchEvents();
        return;
      }
    }
    
    // Ako ne može da dobije instancu kalendara, osveži stranicu
    console.warn('Ne mogu da pristupim API-ju kalendara, osvežavam stranicu...');
    window.location.reload();
  } catch (error) {
    console.error('Greška prilikom osvežavanja kalendara:', error);
    window.location.reload();
  }
}

// Funkcija za proveru i učitavanje Bootstrap JS-a ako nije dostupan
function ensureBootstrapLoaded() {
  try {
    // Proveri da li je Bootstrap JS dostupan
    if (typeof $.fn.modal === 'undefined') {
      console.warn('Bootstrap JS nije dostupan! Učitavam ga...');
      // Dodaj Bootstrap JS ako nije učitan
      const bootstrapScript = document.createElement('script');
      bootstrapScript.src = 'https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.bundle.min.js';
      bootstrapScript.integrity = 'sha384-Piv4xVNRyMGpqkS2by6br4gNJ7DXjqk09RmUpJ8jgGtD7zP9yug3goQfGII0yAns';
      bootstrapScript.crossOrigin = 'anonymous';
      bootstrapScript.onload = function() {
        console.log('Bootstrap JS uspešno učitan!');
        showModal();
      };
      document.head.appendChild(bootstrapScript);
    } else {
      showModal();
    }
    
    function showModal() {
      const $modal = $(modalSelector);
      
      if ($modal.length === 0) {
        console.error(`Modal sa selektorom ${modalSelector} nije pronađen u DOM-u`);
        return;
      }
      
      // Ukloni aria-hidden atribut pre prikazivanja modala
      $modal.removeAttr('aria-hidden');
      
      // Prikaži modal
      $modal.modal({
        backdrop: 'static',
        keyboard: true,
        focus: true
      });
      
      // Dodaj event listener za zatvaranje modala
      $modal.on('hidden.bs.modal', function() {
        // Vrati fokus na element koji je imao fokus pre otvaranja modala
        if (window.lastFocusedElement) {
          window.lastFocusedElement.focus();
        }
      });
      
      // Sačuvaj trenutno fokusirani element
      window.lastFocusedElement = document.activeElement;
    }
  } catch (error) {
    console.error('Greška prilikom prikazivanja modala:', error);
  }
}

// Funkcija updateEventDate je implementirana u calendar_drag_drop.js fajlu
// Ovde je uklonjena duplikat implementacija da bi se izbegli konflikti

// Pomoćna funkcija za prikazivanje toast poruka
function showToast(message, type = 'info') {
  // Proveri da li postoji Toastr biblioteka
  if (typeof toastr !== 'undefined') {
    // Koristi Toastr ako je dostupan
    toastr.options = {
      closeButton: true,
      progressBar: true,
      positionClass: 'toast-top-right',
      timeOut: type === 'error' ? 5000 : 3000
    };
    
    return toastr[type](message);
  } else {
    // Jednostavna alternativa ako Toastr nije dostupan
    console.log(`Toast (${type}):`, message);
    alert(message);
    return null;
  }
}

// Pomoćna funkcija za sakrivanje toast poruka
function hideToast(toast) {
  if (typeof toastr !== 'undefined' && toast) {
    toastr.clear(toast);
  }
}

// Pomoćna funkcija za osvežavanje kalendara
function refreshCalendar() {
  try {
    // Pronađi instancu kalendara
    const calendarEl = document.getElementById('calendar');
    if (calendarEl) {
      // Koristi FullCalendar v5 API za osvežavanje događaja
      const calendarApi = calendarEl._calendar;
      if (calendarApi && typeof calendarApi.refetchEvents === 'function') {
        console.log('Osvežavanje kalendara pomoću FullCalendar v5 API-ja');
        calendarApi.refetchEvents();
        return;
      }
    }
    
    console.warn('Nije moguće osvežiti kalendar direktno, osvežavanje stranice...');
    // Ako ne možemo direktno osvežiti kalendar, osvežimo stranicu
    window.location.reload();
  } catch (error) {
    console.error('Greška prilikom osvežavanja kalendara:', error);
    window.location.reload();
  }
}

// Pomoćna funkcija za dobijanje CSRF tokena
function getCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value || 
         document.cookie.replace(/(?:(?:^|.*;\s*)csrftoken\s*\=\s*([^;]*).*$)|^.*$/, "$1");
}

function initializeCalendar() {
  // Handle all_day checkbox to toggle time fields
  $('#all_day').change(function() {
    if($(this).is(':checked')) {
      // Disable time part for all-day events
      $('#start_datetime').attr('type', 'date');
      $('#end_datetime').attr('type', 'date');
    } else {
      // Enable time part for regular events
      $('#start_datetime').attr('type', 'datetime-local');
      $('#end_datetime').attr('type', 'datetime-local');
    }
  });
  
  // Toggle meeting link based on is_online checkbox
  $('#is_online').change(function() {
    if($(this).is(':checked')) {
      $('#meeting_link_group').show();
    } else {
      $('#meeting_link_group').hide();
    }
  });
  
  // Contact persons management
  var selectedContacts = [];
  
  // Handle company change to load contacts
  $('#company').change(function() {
    const companyId = $(this).val();
    if (!companyId) {
      // Clear contacts
      selectedContacts = [];
      updateContactPersonsField();
      return;
    }
    
    // Load contacts for autocomplete
    $.ajax({
      url: contactsApiUrl,
      data: {
        company_id: companyId
      },
      success: function(data) {
        // Set up autocomplete with jQuery UI
        $("#contact_person").autocomplete({
          source: data.contacts.map(function(contact) {
            return {
              label: contact.ime_prezime + (contact.pozicija ? ' (' + contact.pozicija + ')' : ''),
              value: contact.ime_prezime,
              id: contact.id
            };
          }),
          minLength: 0,
          select: function(event, ui) {
            // Add to selected contacts if not already there
            if (!selectedContacts.some(c => c.id === ui.item.id)) {
              selectedContacts.push({
                id: ui.item.id,
                name: ui.item.value
              });
              updateContactPersonsField();
            }
            // Clear the input
            $(this).val('');
            return false;
          }
        }).focus(function() {
          // Show all options on focus
          $(this).autocomplete("search", "");
        });
      }
    });
  });
  
  // Update the hidden field and display tags
  function updateContactPersonsField() {
    // Update hidden field
    $('#contact_persons').val(selectedContacts.map(c => c.id).join(','));
    
    // Update visual tags
    var tagsHtml = '';
    selectedContacts.forEach(function(contact, index) {
      tagsHtml += '<span class="contact-tag">' + contact.name + 
                  '<span class="remove-contact" data-index="' + index + '">&times;</span></span>';
    });
    $('#contact-tags-container').html(tagsHtml);
    
    // Add click handlers for removing tags
    $('.remove-contact').click(function() {
      var index = $(this).data('index');
      selectedContacts.splice(index, 1);
      updateContactPersonsField();
    });
  }
  
  // Initialize FullCalendar
  var calendarEl = document.getElementById('calendar');
  var calendar = new FullCalendar.Calendar(calendarEl, {
    locale: 'sr',
    initialView: 'dayGridMonth',
    height: 'auto',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    themeSystem: 'bootstrap',
    events: eventsApiUrl,
    editable: true,
    selectable: true,
    selectMirror: true,
    dayMaxEvents: true,
    eventTimeFormat: {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    },
    // In FullCalendar 5.x, plugins are automatically loaded when their scripts are included
    // We don't need to explicitly list them here
    // Allow selecting date range to create appointment
    select: function(info) {
      openNewAppointmentModal(info.startStr, info.endStr, info.allDay);
    },
    // Allow dragging and resizing events
    eventDrop: function(info) {
      handleEventDateChange(info);
    },
    eventResize: function(info) {
      handleEventDateChange(info);
    },
    
    // Handle clicks on dates in the calendar
    dateClick: function(info) {
      // Open new appointment modal with the selected date
      openNewAppointmentModal(info.dateStr, null, true);
    },
    // Show appointment details when clicking on event
    eventClick: function(info) {
      console.log('Event clicked:', info.event);
      
      // Prevent default action (URL navigation)
      info.jsEvent.preventDefault();
      
      // Get event properties
      const eventProps = info.event.extendedProps || {};
      const eventType = eventProps.type || eventProps.eventType;
      console.log('Event type:', eventType);
      console.log('Event extended props:', eventProps);
      console.log('Event ID:', info.event.id);
      
      // Detaljno logovanje za debug
      console.log('Event title:', info.event.title);
      console.log('Event start:', info.event.start);
      console.log('Event end:', info.event.end);
      console.log('Event allDay:', info.event.allDay);
      
      // Provera da li su modalni dijalozi dostupni
      console.log('auditDetailModal dostupan:', $('#auditDetailModal').length > 0);
      console.log('cycleAuditModal dostupan:', $('#cycleAuditModal').length > 0);
      console.log('appointmentDetailModal dostupan:', $('#appointmentDetailModal').length > 0);
      
      // Funkcija za direktno otvaranje modalnih dijaloga iz eventClick handlera
      function safeOpenModal(modalId, event) {
        console.log('Sigurno otvaranje modala:', modalId, 'za događaj:', event);
        
        // Proveri da li modal postoji u DOM-u
        const $modal = $('#' + modalId);
        if ($modal.length === 0) {
          console.error('Modal sa ID-om ' + modalId + ' nije pronađen u DOM-u!');
          alert('Greška: Modal ' + modalId + ' nije pronađen. Osvježite stranicu ili kontaktirajte administratora.');
          return false;
        }
        
        // Pokušaj otvoriti modal na više načina
        try {
          // 1. Pokušaj sa Bootstrap modal funkcijom
          if (typeof $.fn.modal === 'function') {
            console.log('Otvaranje modala kroz Bootstrap API');
            $modal.modal('show');
          } else {
            console.warn('Bootstrap modal funkcija nije dostupna!');
          }
          
          // 2. Direktno podešavanje CSS-a za sigurnost
          setTimeout(function() {
            console.log('Primena direktnih CSS stilova na modal');
            $modal.css({
              'display': 'block',
              'visibility': 'visible',
              'opacity': '1',
              'z-index': '1050'
            }).addClass('show');
            
            // Dodaj backdrop ako ne postoji
            if ($('.modal-backdrop').length === 0) {
              $('body').addClass('modal-open').append('<div class="modal-backdrop fade show"></div>');
            }
          }, 50);
          
          return true;
        } catch (error) {
          console.error('Greška pri otvaranju modala:', error);
          return false;
        }
      }

      // Poboljšana logika za otvaranje odgovarajućeg modalnog dijaloga
      if (eventType === 'audit_day') {
        // Open audit day modal
        console.log('Otvaranje modala za audit dan');
        
        // Prvo zaustavi propagaciju događaja i default ponašanje
        info.jsEvent.stopPropagation();
        info.jsEvent.preventDefault();
        
        // Prvo popuni podatke u modalu
        openAuditDayModal(info.event);
        // Zatim koristi robusnu funkciju za otvaranje modala
        safeOpenModal('auditDayModal', info.event);
        
        // Pokušaj i sa globalnom funkcijom ako je dostupna
        if (typeof window.testOpenModal === 'function') {
          setTimeout(() => window.testOpenModal('auditDayModal'), 100);
        }
        return false;
      } else if (eventType === 'cycle_audit') {
        // Open cycle audit modal
        console.log('Otvaranje modala za certifikacioni ciklus');
        
        // Prvo zaustavi propagaciju događaja i default ponašanje
        info.jsEvent.stopPropagation();
        info.jsEvent.preventDefault();
        
        const cycleId = eventProps.cycle_id;
        console.log('Opening cycle audit modal for cycle ID:', cycleId);
        // Prvo popuni podatke u modalu
        openCycleAuditModal(info.event);
        // Zatim koristi robusnu funkciju za otvaranje modala
        safeOpenModal('cycleAuditModal', info.event);
        
        // Pokušaj i sa globalnom funkcijom ako je dostupna
        if (typeof window.testOpenModal === 'function') {
          setTimeout(() => window.testOpenModal('cycleAuditModal'), 100);
        }
        return false;
      } else if (eventType === 'appointment') {
        // Open appointment modal
        console.log('Otvaranje modala za sastanak');
        
        // Prvo zaustavi propagaciju događaja i default ponašanje
        info.jsEvent.stopPropagation();
        info.jsEvent.preventDefault();
        
        // Prvo popuni podatke u modalu
        openAppointmentModal(info.event);
        // Zatim koristi robusnu funkciju za otvaranje modala
        safeOpenModal('appointmentDetailModal', info.event);
        
        // Pokušaj i sa globalnom funkcijom ako je dostupna
        if (typeof window.testOpenModal === 'function') {
          setTimeout(() => window.testOpenModal('appointmentDetailModal'), 100);
        }
        return false;
      } else {
        // Zaustavi propagaciju i default ponašanje za sve tipove događaja
        info.jsEvent.stopPropagation();
        info.jsEvent.preventDefault();
        
        console.log('Nedefinisan tip događaja, pokušaj identifikacije po svojstvima:', info.event);
        
        // Provera da li događaj ima URL koji ukazuje na tip
        if (info.event.url) {
          console.log('Događaj ima URL:', info.event.url);
          
          // Proveri da li URL ukazuje na audit, appointment ili cycle
          if (info.event.url.includes('audit')) {
            console.log('Događaj je verovatno audit');
            openAuditDayModal(info.event);
            safeOpenModal('auditDayModal', info.event);
            return false;
          } else if (info.event.url.includes('appointment')) {
            console.log('Događaj je verovatno termin');
            openAppointmentModal(info.event);
            safeOpenModal('appointmentDetailModal', info.event);
            return false;
          } else if (info.event.url.includes('cycle')) {
            console.log('Događaj je verovatno ciklus');
            openCycleAuditModal(info.event);
            safeOpenModal('cycleAuditModal', info.event);
            return false;
          }
        }
        
        // Pokušaj izvlačenje ID-a iz različitih izvora
        let auditId = null;
        
        // 1. Prvo iz ID-a događaja
        const idParts = info.event.id ? info.event.id.split('_') : [];
        if (idParts.length > 0) {
          const lastPart = idParts[idParts.length - 1];
          if (!isNaN(parseInt(lastPart))) {
            auditId = parseInt(lastPart);
            console.log('Extracted audit ID from event ID:', auditId);
          }
        }
        
        // 2. Iz extendedProps
        if (!auditId && info.event.extendedProps) {
          const props = info.event.extendedProps;
          auditId = props.audit_id || props.id || (props.url ? props.url.split('/').filter(Boolean).pop() : null);
          console.log('Extracted ID from extendedProps:', auditId);
        }
        
        // Ako je identifikovan ID audita
        if (auditId) {
          console.log('Pokušaj otvaranja modala za audit ID:', auditId);
          openAuditDayModal({id: auditId, extendedProps: {audit_id: auditId}});
          safeOpenModal('auditDayModal', info.event);
        } else {
          console.error('Nije moguće pronaći ID događaja. Događaj:', info.event);
          alert('Greška pri identifikaciji događaja. Molimo osvježite stranicu i pokušajte ponovno.');
        }
      }
      
      return false; // Prevent URL navigation
    },
    // Apply custom styling based on appointment type and status
    eventDidMount: function(info) {
      const event = info.event;
      const eventEl = info.el;
      const extendedProps = event.extendedProps;
      
      // Add event type as a class for styling
      if (extendedProps.eventType === 'audit') {
        $(eventEl).addClass('audit-event');
        
        // Add audit status as data attribute
        if (extendedProps.auditStatus) {
          $(eventEl).attr('data-audit-status', extendedProps.auditStatus);
        }
        
        // Add specific audit type class
        if (extendedProps.type === 'Prva nadzorna provera') {
          $(eventEl).addClass('audit-first');
        } else if (extendedProps.type === 'Druga nadzorna provera') {
          $(eventEl).addClass('audit-second');
        } else if (extendedProps.type === 'Resertifikacija') {
          $(eventEl).addClass('audit-recert');
        }
        
        // Add icon to audit events
        const titleEl = $(eventEl).find('.fc-event-title');
        
        // Different icons for planned vs completed audits
        if (extendedProps.auditStatus === 'completed') {
          titleEl.prepend('<i class="fas fa-check-circle me-1"></i>');
        } else {
          titleEl.prepend('<i class="fas fa-clipboard-check me-1"></i>');
        }
      } else {
        // Regular appointment styling
        $(eventEl).addClass('appointment-event');
        
        // Add icon based on appointment type
        const titleEl = $(eventEl).find('.fc-event-title');
        
        if (extendedProps.type === 'Sastanak') {
          titleEl.prepend('<i class="fas fa-users me-1"></i>');
        } else if (extendedProps.type === 'Poseta') {
          titleEl.prepend('<i class="fas fa-building me-1"></i>');
        } else if (extendedProps.type === 'Poziv') {
          titleEl.prepend('<i class="fas fa-phone me-1"></i>');
        } else {
          titleEl.prepend('<i class="fas fa-calendar-check me-1"></i>');
        }
      }
      
      // Add tooltip with details
      let tooltipContent = `
        <strong>${event.title}</strong><br>
        <strong>Kompanija:</strong> ${extendedProps.company}<br>
        <strong>Tip:</strong> ${extendedProps.type}<br>
        <strong>Status:</strong> ${extendedProps.status || 'N/A'}<br>
      `;
      
      // Add location only for appointments
      if (extendedProps.eventType === 'appointment' && extendedProps.location) {
        tooltipContent += `<strong>Lokacija:</strong> ${extendedProps.location}<br>`;
      }
      
      // Add audit status for audit events and audit days
      if ((extendedProps.eventType === 'audit' || extendedProps.eventType === 'audit_day') && extendedProps.auditStatus) {
        const statusText = extendedProps.auditStatus === 'completed' ? 'Održana' : 'Planirana';
        tooltipContent += `<strong>Status audita:</strong> ${statusText}<br>`;
      }
      
      // Add audit ID for audit days
      if (extendedProps.eventType === 'audit_day' && extendedProps.audit_id) {
        tooltipContent += `<strong>ID audita:</strong> ${extendedProps.audit_id}<br>`;
      }
      
      $(eventEl).tooltip({
        title: tooltipContent,
        html: true,
        placement: 'top',
        container: 'body'
      });
    }
  });
  
  // Render the calendar
  try {
    calendar.render();
    console.log('Calendar rendered successfully');
  } catch (e) {
    console.error('Error rendering calendar:', e);
  }
  
  // Fix calendar rendering
  setTimeout(function() {
    try {
      calendar.updateSize();
      console.log('Calendar size updated');
    } catch (e) {
      console.error('Error updating calendar size:', e);
    }
  }, 200);
  
  // Create new appointment button
  $('#createAppointmentBtn').click(function() {
    openNewAppointmentModal();
  });
  
  // Test audit modal button
  $('#testAuditModalBtn').click(function() {
    console.log('Test audit modal clicked');
    
    try {
      // Popuni modal sa test podacima
      $('#audit-company').text('Test kompanija');
      $('#audit-type').text('Inicijalni audit');
      $('#audit-status').text('Planiran');
      $('#audit-planned-date').text('01.07.2025.');
      $('#audit-actual-date').text('Nije postavljen');
      $('#audit-days-count').text('3');
      $('#audit-notes').text('Test napomena');
      $('#audit-days-list').html('<div class="list-group-item">Test dan audita</div>');
      
      // Pokušaj otvoriti modal
      console.log('Pokušavam otvoriti modal...');
      $('#auditDetailModal').modal('show');
    } catch (e) {
      console.error('Greška prilikom otvaranja modala:', e);
    }
  });
  
  // Test simple modal button
  $('#testSimpleModalBtn').click(function() {
    console.log('Test simple modal clicked');
    try {
      $('#simpleTestModal').modal('show');
    } catch (e) {
      console.error('Greška prilikom otvaranja jednostavnog modala:', e);
    }
  });
  
  // Open new appointment modal
  function openNewAppointmentModal(startDate, endDate, allDay) {
    resetAppointmentForm();
    
    $('#appointmentModalLabel').text('Novi sastanak');
    $('#deleteAppointmentBtn').hide();
    
    if (startDate) {
      $('#start_datetime').val(formatDateTimeForInput(startDate));
      $('#end_datetime').val(formatDateTimeForInput(endDate || addHoursToDate(startDate, 1)));
      $('#all_day').prop('checked', allDay).trigger('change');
    } else {
      // Default to current time + 1 hour
      const now = new Date();
      $('#start_datetime').val(formatDateTimeForInput(now));
      $('#end_datetime').val(formatDateTimeForInput(addHoursToDate(now, 1)));
    }
    
    $('#appointmentModal').modal('show');
  }
  
  // Open appointment detail modal
  function openAppointmentDetailModal(appointmentId) {
    $.ajax({
      url: appointmentDetailUrl.replace('0', appointmentId),
      success: function(data) {
        $('#appointmentDetailContent').html(data);
        $('#appointmentDetailModal').modal('show');
        
        // Set up edit button
        $('#editAppointmentBtn').data('id', appointmentId);
      }
    });
  }
  
  // Open audit detail modal
  function openAuditDetailModal(auditId) {
    console.log('Opening audit detail modal for ID:', auditId);
    
    // Umesto JSON-a, otvori direktno link u novom tabu
    const auditDetailUrl = `/company/audits/${auditId}/`;
    console.log('Redirecting to URL:', auditDetailUrl);
    
    // Jednostavno otvori URL u novom tabu umesto da pokušavamo da učitamo preko AJAX-a
    window.open(auditDetailUrl, '_blank');
  }
  
  // Edit appointment button
  $('#editAppointmentBtn').click(function() {
    const appointmentId = $(this).data('id');
    $('#appointmentDetailModal').modal('hide');
    openEditAppointmentModal(appointmentId);
  });
  
  // Open edit appointment modal
  function openEditAppointmentModal(appointmentId) {
    resetAppointmentForm();
    
    $.ajax({
      url: appointmentUpdateUrl.replace('0', appointmentId),
      success: function(data) {
        // Fill form with appointment data
        $('#appointmentId').val(appointmentId);
        $('#appointmentModalLabel').text('Izmeni sastanak');
        $('#deleteAppointmentBtn').show();
        
        // Parse HTML response to extract form values
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = data;
        
        // Extract form data
        const appointment = JSON.parse(tempDiv.querySelector('#appointment-data').textContent);
        
        // Fill form fields
        $('#title').val(appointment.title);
        $('#company').val(appointment.company_id).trigger('change');
        $('#appointment_type').val(appointment.appointment_type);
        $('#start_datetime').val(formatDateTimeForInput(appointment.start_datetime));
        $('#end_datetime').val(formatDateTimeForInput(appointment.end_datetime));
        $('#all_day').prop('checked', appointment.all_day).trigger('change');
        $('#location').val(appointment.location);
        $('#is_online').prop('checked', appointment.is_online).trigger('change');
        $('#meeting_link').val(appointment.meeting_link);
        $('#status').val(appointment.status);
        $('#notes').val(appointment.notes);
        $('#external_attendees').val(appointment.external_attendees);
        
        // Set selected contact persons
        setTimeout(function() {
          const contactData = JSON.parse(tempDiv.querySelector('#selected-contacts').textContent);
          selectedContacts = contactData.map(id => {
            const contactEl = tempDiv.querySelector(`[data-contact-id="${id}"]`);
            return {
              id: id,
              name: contactEl ? contactEl.textContent : `Contact #${id}`
            };
          });
          updateContactPersonsField();
        }, 500);
        
        $('#appointmentModal').modal('show');
      }
    });
  }
  
  // Reset appointment form
  function resetAppointmentForm() {
    $('#appointmentForm')[0].reset();
    $('#appointmentId').val('');
    $('#company').val('').trigger('change');
    $('#meeting_link_group').hide();
    selectedContacts = [];
    updateContactPersonsField();
  }
  
  // Handle appointment form submission
  $('#appointmentForm').submit(function(e) {
    e.preventDefault();
    
    const appointmentId = $('#appointmentId').val();
    const isNewAppointment = !appointmentId;
    
    const formData = {
      title: $('#title').val(),
      company: $('#company').val(),
      appointment_type: $('#appointment_type').val(),
      start_datetime: $('#start_datetime').val(),
      end_datetime: $('#end_datetime').val(),
      all_day: $('#all_day').is(':checked') ? 'on' : '',
      location: $('#location').val(),
      is_online: $('#is_online').is(':checked') ? 'on' : '',
      meeting_link: $('#meeting_link').val(),
      status: $('#status').val(),
      notes: $('#notes').val(),
      contact_persons: $('#contact_persons').val().split(',').filter(Boolean),
      external_attendees: $('#external_attendees').val()
    };
    
    const url = isNewAppointment 
      ? appointmentCreateUrl
      : appointmentUpdateUrl.replace('0', appointmentId);
    
    $.ajax({
      url: url,
      method: 'POST',
      data: formData,
      headers: {
        'X-CSRFToken': getCsrfToken()
      },
      success: function(response) {
        $('#appointmentModal').modal('hide');
        calendar.refetchEvents();
      },
      error: function(xhr) {
        alert('Došlo je do greške prilikom čuvanja sastanka.');
        console.error(xhr.responseText);
      }
    });
  });
  
  // Handle appointment deletion
  $('#deleteAppointmentBtn').click(function() {
    if (!confirm('Da li ste sigurni da želite da obrišete ovaj sastanak?')) {
      return;
    }
    
    const appointmentId = $('#appointmentId').val();
    
    $.ajax({
      url: appointmentDeleteUrl.replace('0', appointmentId),
      method: 'POST',
      headers: {
        'X-CSRFToken': getCsrfToken()
      },
      success: function(response) {
        $('#appointmentModal').modal('hide');
        calendar.refetchEvents();
      },
      error: function(xhr) {
        alert('Došlo je do greške prilikom brisanja sastanka.');
        console.error(xhr.responseText);
      }
    });
  });
  
  // Update appointment dates when dragged or resized
  function updateAppointmentDates(event) {
    const appointmentId = event.id;
    const formData = {
      start_datetime: event.start.toISOString(),
      end_datetime: event.end ? event.end.toISOString() : null,
      all_day: event.allDay ? 'on' : ''
    };
    
    $.ajax({
      url: appointmentUpdateUrl.replace('0', appointmentId),
      method: 'POST',
      data: formData,
      headers: {
        'X-CSRFToken': getCsrfToken()
      },
      error: function(xhr) {
        alert('Došlo je do greške prilikom ažuriranja datuma sastanka.');
        console.error(xhr.responseText);
        calendar.refetchEvents();
      }
    });
  }
  
  // Edit audit button
  $('#editAuditBtn').click(function() {
    const auditId = $(this).data('id');
    $('#auditDetailModal').modal('hide');
    window.location.href = auditUpdateUrl.replace('0', auditId);
  });

  // Funkcija za formatiranje datuma u lokalni format
  function formatDate(dateString) {
    if (!dateString) return '';
    return moment(dateString).format('DD.MM.YYYY.');
  }

  // Funkcija za otvaranje modala za detalje certifikacionog ciklusa
  function openCycleAuditModal(event) {
    console.log('Opening cycle audit modal for event:', event);
    console.log('Event extended props:', event.extendedProps);
    
    try {
      // Prikaži modal
      $('#cycleAuditModal').modal('show');
      
      // Postavi učitavanje za sva polja
      $('#cycle-company').text('Učitavanje...');
      $('#cycle-audit-type').text('Učitavanje...');
      $('#cycle-status').text('Učitavanje...');
      $('#cycle-planned-date').text('Učitavanje...');
      $('#cycle-actual-date').text('Učitavanje...');
      $('#cycle-id').text('Učitavanje...');
      $('#cycle-start-date').text('Učitavanje...');
      $('#cycle-end-date').text('Učitavanje...');
      $('#cycle-cycle-status').text('Učitavanje...');
      $('#cycle-notes').text('Učitavanje...');
      
      // Dobavi podatke iz event objekta
      const eventProps = event.extendedProps || {};
      const cycleId = eventProps.cycle_id;
      
      console.log('Cycle ID from event:', cycleId);
      console.log('Event ID:', event.id);
      
      if (!cycleId) {
        console.error('Nije pronađen ID ciklusa u event objektu');
        $('#cycle-company').text('Greška: Nije pronađen ID ciklusa');
        return;
      }
      
      // Popuni osnovne podatke iz event objekta
      $('#cycle-company').text(eventProps.company || 'N/A');
      $('#cycle-audit-type').text(eventProps.type || 'N/A');
      $('#cycle-status').text(eventProps.status || 'N/A');
      $('#cycle-id').text(cycleId || 'N/A');
      $('#cycle-notes').text(eventProps.notes || 'Nema napomena');
      
      // Postavi URL za dugme za pregled ciklusa
      $('#viewCycleBtn').off('click').on('click', function() {
        const cycleUrl = `/company/cycles/${cycleId}/`;
        console.log('Navigating to cycle URL:', cycleUrl);
        window.location.href = cycleUrl;
      });
      
      // Postavi URL za dugme za izmenu audita
      let auditId;
      try {
        auditId = event.id.split('_').pop();
        console.log('Extracted audit ID:', auditId);
      } catch (e) {
        console.error('Error extracting audit ID:', e);
        auditId = '';
      }
      
      $('#editCycleAuditBtn').off('click').on('click', function() {
        const auditUrl = `/company/audits/${auditId}/update/`;
        console.log('Navigating to audit update URL:', auditUrl);
        window.location.href = auditUrl;
      });
      
      // Proveri da li je URL za dohvatanje podataka o ciklusu dostupan
      if (!certificationCycleJsonUrl) {
        console.error('certificationCycleJsonUrl nije definisan');
        $('#cycle-start-date').text('Greška: URL nije dostupan');
        $('#cycle-end-date').text('Greška: URL nije dostupan');
        $('#cycle-cycle-status').text('Greška: URL nije dostupan');
        return;
      }
      
      const ajaxUrl = certificationCycleJsonUrl.replace('0', cycleId);
      console.log('AJAX URL for cycle data:', ajaxUrl);
      
      // Dohvati dodatne podatke o ciklusu preko AJAX-a
      $.ajax({
        url: ajaxUrl,
        dataType: 'json',
        timeout: 10000, // 10 sekundi timeout
        beforeSend: function() {
          console.log('Sending AJAX request for cycle data...');
        },
        success: function(data) {
          console.log('Cycle data received:', data);
          
          if (data && data.cycle) {
            // Popuni podatke o ciklusu
            $('#cycle-start-date').text(formatDate(data.cycle.start_date));
            $('#cycle-end-date').text(formatDate(data.cycle.end_date));
            $('#cycle-cycle-status').text(data.cycle.status_display || 'N/A');
            
            // Popuni podatke o auditu
            if (data.audit) {
              $('#cycle-planned-date').text(formatDate(data.audit.planned_date) || 'Nije postavljen');
              $('#cycle-actual-date').text(formatDate(data.audit.actual_date) || 'Nije postavljen');
            } else {
              console.warn('Nema podataka o auditu u odgovoru');
              $('#cycle-planned-date').text('Nije dostupno');
              $('#cycle-actual-date').text('Nije dostupno');
            }
          } else {
            console.error('Nema podataka o ciklusu u odgovoru');
            $('#cycle-start-date').text('Nije dostupno');
            $('#cycle-end-date').text('Nije dostupno');
            $('#cycle-cycle-status').text('Nije dostupno');
          }
        },
        error: function(xhr, status, error) {
          console.error('Greška prilikom dohvatanja podataka o ciklusu:', error);
          console.error('Status:', status);
          console.error('Response text:', xhr.responseText);
          
          let errorMsg = 'Greška prilikom dohvatanja podataka';
          
          try {
            const response = JSON.parse(xhr.responseText);
            if (response && response.error) {
              errorMsg = response.error;
            }
          } catch (e) {
            console.error('Greška prilikom parsiranja odgovora:', e);
          }
          
          $('#cycle-start-date').text('Greška');
          $('#cycle-end-date').text('Greška');
          $('#cycle-cycle-status').text('Greška');
          alert('Greška prilikom dohvatanja podataka o ciklusu: ' + errorMsg);
        }
      });
    } catch (e) {
      console.error('Greška pri otvaranju CycleAudit modala:', e);
    }
  }

  // Helper functions
  function formatDateTimeForInput(date) {
    if (!date) return '';
    
    if (typeof date === 'string') {
      date = new Date(date);
    }
    
    // Format for HTML datetime-local input (YYYY-MM-DDThh:mm)
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  }
  
  function addHoursToDate(date, hours) {
    if (typeof date === 'string') {
      date = new Date(date);
    }
    
    const newDate = new Date(date);
    newDate.setHours(newDate.getHours() + hours);
    return newDate;
  }
  
  function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
  }
}

/**
 * Globalni modalObserver - prati i rešava probleme sa modalnim prozorima u realnom vremenu
 * Ova funkcija postavlja observera koji automatski reaguje na promene modalnih prozora
 * i rešava probleme sa backdrop elementima i scrollom
 */
function setupModalObserver() {
  console.log('Postavljanje globalnog modal observer-a...');
  
  // Pratimo promene na body elementu
  const targetNode = document.body;
  const config = { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'style'] };
  
  // Funkcija koja reaguje na promene
  const callback = function(mutationsList, observer) {
    for (const mutation of mutationsList) {
      // Detektuj promene koje se odnose na modalne prozore
      if ((mutation.type === 'childList' && 
          Array.from(mutation.addedNodes).some(node => 
            node.nodeType === 1 && (node.classList?.contains('modal-backdrop') || 
                                   node.classList?.contains('modal')))) ||
          (mutation.type === 'attributes' && 
           mutation.target.classList?.contains('modal'))) {
        
        // Proveri da li je neki modal otvoren
        const openModals = document.querySelectorAll('.modal.show');
        const hasOpenModals = openModals.length > 0;
        
        // Proveri backdrop elemente
        const backdrops = document.querySelectorAll('.modal-backdrop');
        
        // Ako imamo više backdrop-ova nego otvorenih modala, imamo problem
        if (backdrops.length > openModals.length) {
          console.log(`Detektovan višak backdrop-ova: ${backdrops.length} > ${openModals.length}`);
          cleanupModalBackdrops(true);
        }
        
        // Ako je otvoren modal, osiguraj pravilno stanje stranice
        if (hasOpenModals) {
          // Osiguraj da je body u modal-open stanju
          document.documentElement.classList.add('modal-open-html');
          document.body.classList.add('modal-open');
          
          // Osiguraj da svi modali imaju pravilne z-index vrednosti
          openModals.forEach(modal => {
            modal.style.zIndex = '2050';
          });
        } else {
          // Ako nema otvorenih modala, resetuj stanje stranice
          if (document.body.classList.contains('modal-open') && backdrops.length === 0) {
            // Pozovi naš handler za resetovanje stanja stranice
            // Koristimo resetBodyState funkciju ako je dostupna, ili manuelno resetujemo
            if (typeof resetBodyState === 'function') {
              resetBodyState();
            } else {
              document.documentElement.classList.remove('modal-open-html');
              document.body.classList.remove('modal-open');
              document.body.style.removeProperty('padding-right');
              document.body.style.removeProperty('overflow');
            }
          }
        }
      }
    }
  };
  
  // Kreiraj i pokreni observer
  const observer = new MutationObserver(callback);
  observer.observe(targetNode, config);
  
  console.log('Globalni modal observer postavljen');
  return observer;
}

// Pokreni observer kad se stranica učita
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(() => {
    setupModalObserver();
    // Takođe periodično čisti backdrop elemente svakih 5 sekundi
    setInterval(() => {
      if (document.querySelectorAll('.modal.show').length === 0) {
        cleanupModalBackdrops(true);
      }
    }, 5000);
  }, 500);
});
