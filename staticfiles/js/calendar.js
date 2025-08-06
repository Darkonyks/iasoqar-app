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
  
  // Dodaj backdrop ako ne postoji
  if (!document.querySelector('.modal-backdrop')) {
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop fade show';
    document.body.appendChild(backdrop);
  }
  
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
    
    // Dodaj backdrop ako ne postoji
    if (!document.querySelector('.modal-backdrop')) {
      const backdrop = document.createElement('div');
      backdrop.className = 'modal-backdrop fade show';
      document.body.appendChild(backdrop);
    }
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

// Funkcija za otvaranje modala za detalje audit dana
function openAuditDayModal(event) {
  console.log('Opening audit day modal for event (Bootstrap 5):', event);
  console.log('Event extended props:', event.extendedProps);
  
  try {
    // Napomena: Modal se sada otvara u eventClick handleru koristeći Bootstrap 5 API
    // Stari jQuery način više nije potreban jer se modal otvara u eventClick handleru
    // const modalElement = document.getElementById('auditDetailModal');
    // const auditModal = new bootstrap.Modal(modalElement);
    // auditModal.show();
    
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

// Funkcija za otvaranje modala za detalje certifikacionog ciklusa
function openCycleAuditModal(event) {
  console.log('Opening cycle audit modal for event:', event);
  console.log('Event extended props:', event.extendedProps);
  
  try {
    // Napomena: Modal se sada otvara u eventClick handleru koristeći Bootstrap 5 API
    // Stari način otvaranja modala više nije potreban jer se modal otvara u eventClick handleru
    // const modalElement = document.getElementById('cycleAuditModal');
    // const cycleModal = new bootstrap.Modal(modalElement);
    // cycleModal.show();
    
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

// Funkcija za otvaranje modala za detalje termina
function openAppointmentModal(event) {
  console.log('Opening appointment modal for event (Bootstrap 5):', event);
  console.log('Event extended props:', event.extendedProps);
  
  try {
    // Napomena: Modal se sada otvara u eventClick handleru koristeći Bootstrap 5 API
    // Stari jQuery način više nije potreban jer se modal otvara u eventClick handleru
    // const modalElement = document.getElementById('appointmentDetailModal');
    // const appointmentModal = new bootstrap.Modal(modalElement);
    // appointmentModal.show();
    
    // Postavi učitavanje za sva polja
    $('#appointment-title').text('Učitavanje...');
    $('#appointment-company').text('Učitavanje...');
    $('#appointment-start').text('Učitavanje...');
    $('#appointment-end').text('Učitavanje...');
    $('#appointment-location').text('Učitavanje...');
    $('#appointment-description').text('Učitavanje...');
    $('#appointment-contacts').text('Učitavanje...');
    
    // Dobavi podatke iz event objekta
    const eventProps = event.extendedProps || {};
    const appointmentId = eventProps.appointment_id;
    
    console.log('Appointment ID from event:', appointmentId);
    
    if (!appointmentId) {
      console.error('Nije pronađen ID termina u event objektu');
      $('#appointment-title').text('Greška: Nije pronađen ID termina');
      return;
    }
    
    // Popuni osnovne podatke iz event objekta
    $('#appointment-title').text(event.title || 'N/A');
    $('#appointment-company').text(eventProps.company || 'N/A');
    $('#appointment-start').text(formatDate(event.start) + ' ' + event.start.toLocaleTimeString('sr-RS'));
    $('#appointment-end').text(formatDate(event.end) + ' ' + event.end.toLocaleTimeString('sr-RS'));
    $('#appointment-location').text(eventProps.location || 'Nije definisano');
    $('#appointment-description').text(eventProps.description || 'Nema opisa');
    $('#appointment-contacts').text(eventProps.contacts || 'Nema kontakata');
    
    // Postavi ID za edit dugme
    $('#editAppointmentBtn').data('id', appointmentId);
  } catch (e) {
    console.error('Greška pri otvaranju Appointment modala:', e);
  }
}

// Samo jedna inicijalizacija kalendara kada je dokument spreman
$(document).ready(function() {
  console.log('jQuery document.ready - inicijalizacija kalendara i modala...');
  initializeCalendar();
  initializeModals();
});

// Funkcija za inicijalizaciju modalnih dijaloga
function initializeModals() {
  console.log('Inicijalizacija modalnih dijaloga...');
  
  // Provera da li su modalni dijalozi dostupni u DOM-u
  const auditModalExists = $('#auditDetailModal').length > 0;
  const cycleModalExists = $('#cycleAuditModal').length > 0;
  const appointmentModalExists = $('#appointmentDetailModal').length > 0;
  
  console.log('Modalni dijalozi u DOM-u:', {
    auditDetailModal: auditModalExists,
    cycleAuditModal: cycleModalExists,
    appointmentDetailModal: appointmentModalExists
  });
  
  // Provera da li je Bootstrap modal funkcija dostupna
  const hasBootstrapModal = typeof $.fn.modal === 'function';
  console.log('Bootstrap modal funkcija dostupna:', hasBootstrapModal);
  
  if (hasBootstrapModal) {
    // Inicijalizacija Bootstrap modalnih dijaloga
    if (auditModalExists) {
      $('#auditDetailModal').modal({
        show: false,
        backdrop: 'static',
        keyboard: true
      });
    }
    
    if (cycleModalExists) {
      $('#cycleAuditModal').modal({
        show: false,
        backdrop: 'static',
        keyboard: true
      });
    }
    
    if (appointmentModalExists) {
      $('#appointmentDetailModal').modal({
        show: false,
        backdrop: 'static',
        keyboard: true
      });
    }
  } else {
    console.warn('Bootstrap modal funkcija nije dostupna! Modalni dijalozi neće raditi ispravno.');
    // Pokušaj učitavanja Bootstrap JS-a
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.min.js';
    document.head.appendChild(script);
    script.onload = function() {
      console.log('Bootstrap JS uspešno učitan!');
      // Ponovo inicijalizuj modalne dijaloge
      setTimeout(initializeModals, 500);
    };
  }
  
  // Dodavanje event listenera za klik na događaje u kalendaru
  $(document).on('click', '.fc-event', function(e) {
    console.log('Kliknuto na događaj u kalendaru', e);
  });
  
  // Test otvaranja modala direktno iz JavaScript-a
  window.testOpenModal = function(modalId) {
    console.log('Test otvaranja modala:', modalId);
    $('#' + modalId).modal('show');
    
    // Dodatna provera da li je modal vidljiv
    setTimeout(function() {
      const isVisible = $('#' + modalId).is(':visible');
      console.log(`Modal ${modalId} vidljivost:`, isVisible);
      
      if (!isVisible) {
        // Pokušaj direktno podešavanja CSS-a
        $('#' + modalId).css({
          'display': 'block',
          'visibility': 'visible',
          'opacity': '1',
          'z-index': '1050'
        }).addClass('show');
        $('body').addClass('modal-open');
        
        // Dodaj backdrop ako ne postoji
        if ($('.modal-backdrop').length === 0) {
          $('body').append('<div class="modal-backdrop fade show"></div>');
          // Postavi ispravnu z-index vrednost za backdrop (niža od modala)
          $('.modal-backdrop').css('z-index', '1040'); // Modal je obično na z-index: 1050
        }
      }
    }, 100);
  };
  
  // Test dugmad su uklonjena iz produkcijske verzije
}

// Funkcija za inicijalizaciju kalendara
function initializeCalendar() {
  console.log('Inicijalizacija kalendara...');
  
  // Provera da li je FullCalendar dostupan
  if (typeof FullCalendar === 'undefined') {
    console.error('FullCalendar nije učitan!');
    alert('Greška: FullCalendar biblioteka nije učitana. Osvježite stranicu ili kontaktirajte administratora.');
    return;
  }
  
  // Dohvati element kalendara
  const calendarEl = document.getElementById('calendar');
  if (!calendarEl) {
    console.error('Element kalendara nije pronađen!');
    return;
  }
  
  // Provera da li su potrebni pluginovi dostupni
  console.log('FullCalendar verzija:', FullCalendar.version);
  
  // Inicijalizacija modalnih dijaloga
  initializeModals();
  
  try {
    // Inicijalizacija kalendara sa bundleovanom verzijom FullCalendar-a
    const calendar = new FullCalendar.Calendar(calendarEl, {
      locale: 'sr',
      initialView: 'dayGridMonth',
      height: 'auto',
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
      },
      events: window.eventsApiUrl,
      // Omogućavanje drag-and-drop funkcionalnosti
      editable: true,
      eventStartEditable: true,
      eventDurationEditable: false, // Onemogućavamo promenu trajanja događaja
      eventClick: function(info) {
        // Detaljno logovanje događaja
        console.log('Event clicked:', info.event);
        console.log('Event title:', info.event.title);
        console.log('Event start:', info.event.start);
        console.log('Event end:', info.event.end);
        console.log('Event allDay:', info.event.allDay);
        console.log('Event extendedProps:', info.event.extendedProps);
        
        // Provera oba polja za tip događaja (type i eventType)
        const eventType = info.event.extendedProps?.type || info.event.extendedProps?.eventType;
        console.log('Detected event type:', eventType);
        
        if (eventType === 'appointment') {
          console.log('Otvaranje modala za termin/sastanak');
          openAppointmentModal(info.event);
        } else if (eventType === 'audit_day') {
          console.log('Otvaranje modala za audit dan');
          openAuditDayModal(info.event);
        } else if (eventType === 'cycle_audit') {
          console.log('Otvaranje modala za ciklus audit');
          openCycleAuditModal(info.event);
        } else {
          console.warn('Nepoznat tip događaja:', eventType);
        }
      },
      
      // Handler za drag-and-drop događaja
      eventDrop: function(info) {
        const event = info.event;
        const eventType = event.extendedProps?.type; // Koristimo type umesto eventType
        
        console.log('Događaj premešten:', event);
        console.log('Event extended props:', event.extendedProps);
        
        // Određivanje ID-a događaja u zavisnosti od tipa
        let eventId;
        if (eventType === 'audit_day') {
          eventId = event.extendedProps?.audit_day_id || event.id;
        } else if (eventType === 'appointment') {
          eventId = event.extendedProps?.appointment_id || event.id;
        } else {
          eventId = event.id;
        }
        
        const newDate = event.start;
        
        console.log('Događaj premešten - detalji:', {
          eventType: eventType,
          eventId: eventId,
          newDate: newDate
        });
        
        // Provera da li je dozvoljeno pomeranje ovog tipa događaja
        if (!eventType) {
          console.warn('Nepoznat tip događaja:', eventType);
          info.revert(); // Vrati događaj na originalnu poziciju
          return;
        }
        
        // Podržani tipovi događaja za drag-and-drop
        const supportedTypes = ['audit_day', 'cycle_audit', 'appointment'];
        if (!supportedTypes.includes(eventType)) {
          console.warn('Pomeranje ovog tipa događaja nije podržano:', eventType);
          info.revert(); // Vrati događaj na originalnu poziciju
          return;
        }
        
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
    });
    
    // Renderuj kalendar
    calendar.render();
    console.log('Kalendar uspešno inicijalizovan');
  } catch (error) {
    console.error('Greška pri inicijalizaciji kalendara:', error);
  }
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
  const eventType = event.extendedProps.type;
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
      $modal = $('#dateChangeConfirmationModal');
    }
    
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
    
    // Prikaži modal koristeći Bootstrap 5 API
    try {
      const modalElement = document.getElementById('dateChangeConfirmationModal');
      const dateChangeModal = new bootstrap.Modal(modalElement);
      dateChangeModal.show();
    } catch (error) {
      console.error('Greška pri otvaranju modala za potvrdu promene datuma:', error);
      // Fallback na direktnu DOM manipulaciju ako Bootstrap 5 API nije dostupan
      const modalElement = document.getElementById('dateChangeConfirmationModal');
      modalElement.classList.add('show');
      modalElement.style.display = 'block';
      document.body.classList.add('modal-open');
    }
  }
}

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

// Funkcija za sigurno prikazivanje modala bez problema sa aria-hidden atributom
function safeShowModal(modalSelector) {
  console.log('safeShowModal pozvan za:', modalSelector);
  
  // Proveri da li je selektor validan
  if (!modalSelector || typeof modalSelector !== 'string') {
    console.error('Neispravan selektor modala:', modalSelector);
    return;
  }
  
  // Proveri da li je jQuery dostupan
  if (typeof $ !== 'function') {
    console.error('jQuery nije dostupan!');
    alert('Greška: jQuery nije dostupan. Modalni dijalog se ne može prikazati.');
    return;
  }
  
  // Proveri da li je Bootstrap dostupan
  if (typeof $.fn.modal !== 'function') {
    console.error('Bootstrap modal nije dostupan!');
    alert('Greška: Bootstrap nije ispravno učitan. Modalni dijalog se ne može prikazati.');
    return;
  }
  
  const $modal = $(modalSelector);
  
  // Proveri da li modal postoji u DOM-u
  if ($modal.length === 0) {
    console.error('Modal nije pronađen:', modalSelector);
    alert('Greška: Modalni dijalog ' + modalSelector + ' nije pronađen u DOM-u.');
    return;
  }
  
  console.log('Modal element pronađen:', $modal);
  
  // Proveri da li je modal već prikazan
  if ($modal.hasClass('show')) {
    console.log('Modal je već prikazan');
    return;
  }
  
  // Proveri CSS stilove koji bi mogli blokirati prikaz modala
  checkModalStyles(modalSelector);
  
  // Pokušaj više metoda za otvaranje modala
  tryMultipleModalOpenMethods(modalSelector);
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
    newDate: newDate.toISOString()
  });
  
  // Formatiranje datuma u YYYY-MM-DD format za backend
  const formattedDate = newDate.toISOString().split('T')[0];
  
  // Dobijanje CSRF tokena
  const csrftoken = getCookie('csrftoken');
  
  // Slanje AJAX zahteva za ažuriranje datuma
  $.ajax({
    url: '/company/update-event-date/',
    type: 'POST',
    data: {
      event_type: eventType,
      event_id: eventId,
      new_date: formattedDate
    },
    headers: {
      'X-CSRFToken': csrftoken
    },
    success: function(response) {
      console.log('Uspešno ažuriran datum događaja:', response);
      
      if (response.success) {
        // Prikaži poruku o uspehu
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
        
        // Osveži kalendar
        refreshCalendar();
      } else {
        // Prikaži poruku o grešci
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
      console.error('Greška prilikom ažuriranja datuma događaja:', error);
      console.error('Status:', status);
      console.error('Response text:', xhr.responseText);
      
      // Prikaži poruku o grešci
      if (typeof Swal !== 'undefined') {
        Swal.fire({
          title: 'Greška',
          text: 'Došlo je do greške prilikom ažuriranja datuma događaja.',
          icon: 'error',
          confirmButtonText: 'U redu'
        });
      } else {
        alert('Greška prilikom ažuriranja datuma događaja.');
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
        // Prvo popuni podatke u modalu
        openAuditDayModal(info.event);
        // Zatim koristi robusnu funkciju za otvaranje modala
        safeOpenModal('auditDetailModal', info.event);
        
        // Pokušaj i sa globalnom funkcijom ako je dostupna
        if (typeof window.testOpenModal === 'function') {
          setTimeout(() => window.testOpenModal('auditDetailModal'), 100);
        }
        return false;
      } else if (eventType === 'cycle_audit') {
        // Open cycle audit modal
        console.log('Otvaranje modala za certifikacioni ciklus');
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
        // Pokušaj da izvučeš ID audita iz ID-a događaja
        const idParts = info.event.id.split('_');
        if (idParts.length > 0) {
          const lastPart = idParts[idParts.length - 1];
          if (!isNaN(parseInt(lastPart))) {
            auditId = parseInt(lastPart);
            console.log('Extracted audit ID from event ID:', auditId);
          }
        }
      }
      
      // Ako je pronađen ID audita, otvori modal
      if (auditId) {
        openAuditDetailModal(auditId);
      } else {
        console.error('Nije moguće pronaći ID audita');
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
  
  // Handle window resize to ensure calendar is properly sized
  window.addEventListener('resize', function() {
    try {
      calendar.updateSize();
      console.log('Calendar size updated');
    } catch (e) {
      console.error('Error updating calendar size:', e);
    }
  });

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
    
    // Koristi ispravnu putanju za dohvat detalja audita
    const auditDetailUrl = `/company/audits/${auditId}/`;
    console.log('Using URL:', auditDetailUrl);
    
    // Prikaži modal odmah da korisnik zna da se nešto dešava
    $('#auditDetailModal').modal('show');
    
    // Postavi stanje učitavanja
    $('#audit-company').text('Učitavanje...');
    $('#audit-type').text('Učitavanje...');
    $('#audit-status').text('Učitavanje...');
    $('#audit-planned-date').text('Učitavanje...');
    $('#audit-actual-date').text('Učitavanje...');
    $('#audit-notes').text('Učitavanje...');
    $('#audit-days-table-body').html('<tr><td colspan="4" class="text-center">Učitavanje dana audita...</td></tr>');
    
    $.ajax({
      url: auditDetailUrl, // Koristi direktno URL koji smo definisali iznad
      dataType: 'json',
      timeout: 10000, // 10 sekundi timeout
      success: function(data) {
        console.log('Received audit data:', data);
        
        try {
          // Popuni osnovne informacije o kompaniji
          if (data && data.company) {
            $('#audit-company').text(data.company.name || 'Nije dostupno');
          } else {
            $('#audit-company').text('Nije dostupno');
          }
          
          // Popuni tip i status audita
          $('#audit-type').text(data && data.audit_type_display ? data.audit_type_display : 'Nije dostupno');
          $('#audit-status').text(data && data.audit_status_display ? data.audit_status_display : 'Nije dostupno');
          
          // Popuni datume
          $('#audit-planned-date').text(data && data.planned_date ? formatDate(data.planned_date) : 'Nije postavljen');
          $('#audit-actual-date').text(data && data.actual_date ? formatDate(data.actual_date) : 'Nije postavljen');
          
          // Popuni audit days tabelu
          const auditDaysTableBody = $('#audit-days-table-body');
          auditDaysTableBody.empty();
          
          if (data && data.audit_days && Array.isArray(data.audit_days) && data.audit_days.length > 0) {
            data.audit_days.forEach(function(day) {
              try {
                const row = $('<tr>');
                row.append($('<td>').text(day.date ? formatDate(day.date) : 'Nepoznat datum'));
                row.append($('<td>').text(day.is_planned ? 'Da' : 'Ne'));
                row.append($('<td>').text(day.is_actual ? 'Da' : 'Ne'));
                row.append($('<td>').text(day.notes || '-'));
                auditDaysTableBody.append(row);
              } catch (dayError) {
                console.error('Greška pri obradi dana audita:', dayError);
              }
            });
          } else {
            auditDaysTableBody.append(
              $('<tr>').append(
                $('<td colspan="4" class="text-center">').text('Nema definisanih dana audita')
              )
            );
          }
          
          // Popuni napomene
          $('#audit-notes').text(data && data.notes ? data.notes : 'Nema napomena');
          
          // Postavi ID za edit dugme
          if (data && data.id) {
            $('#editAuditBtn').data('id', data.id);
            $('#editAuditBtn').prop('disabled', false);
          } else {
            $('#editAuditBtn').prop('disabled', true);
          }
        } catch (e) {
          console.error('Greška pri obradi podataka audita:', e);
          $('#audit-company').text('Greška pri obradi podataka');
          $('#audit-days-table-body').html('<tr><td colspan="4" class="text-center">Greška pri obradi podataka</td></tr>');
        }
      },
      error: function(xhr, status, error) {
        console.error('AJAX error:', status, error);
        console.error('Response text:', xhr.responseText);
        $('#audit-company').text('Greška pri učitavanju');
        $('#audit-type').text('Nije dostupno');
        $('#audit-status').text('Nije dostupno');
        $('#audit-planned-date').text('Nije dostupno');
        $('#audit-actual-date').text('Nije dostupno');
        $('#audit-notes').text('Nije dostupno');
        $('#audit-days-table-body').html('<tr><td colspan="4" class="text-center">Greška pri učitavanju podataka</td></tr>');
        
        // Prikaži detalje greške u konzoli i obavesti korisnika
        try {
          const responseData = xhr.responseText ? JSON.parse(xhr.responseText) : {};
          if (responseData && responseData.error) {
            console.error('Server error:', responseData.error);
            alert('Došlo je do greške prilikom učitavanja detalja audita: ' + responseData.error);
          } else {
            alert('Došlo je do greške prilikom učitavanja detalja audita.');
          }
        } catch (e) {
          alert('Došlo je do greške prilikom učitavanja detalja audita.');
        }
      }
    });
  }
  
  // Edit appointment button
  $('#editAppointmentBtn').click(function() {
    const appointmentId = $(this).data('id');
    $('#appointmentDetailModal').modal('hide');
    openEditAppointmentModal(appointmentId);
  });
  
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
