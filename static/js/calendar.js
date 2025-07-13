// Funkcija za sigurno prikazivanje modala koja proverava da li je Bootstrap JS učitan
// i pravilno upravlja fokusom za accessibility
function safeShowModal(modalSelector) {
  try {
    // Sačuvaj element koji trenutno ima fokus da bismo mu vratili fokus kada se modal zatvori
    const previouslyFocusedElement = document.activeElement;
    
    // Proveri da li je Bootstrap JS učitan
    if (typeof $.fn.modal === 'function') {
      // Bootstrap je učitan, prikaži modal
      const $modal = $(modalSelector);
      
      // Ukloni aria-hidden atribut ako postoji da bi izbegao accessibility probleme
      $modal.removeAttr('aria-hidden');
      
      // Prikaži modal
      $modal.modal('show');
      
      // Postavi fokus na prvi fokusabilni element u modalu
      // (nakon što se modal prikaže)
      $modal.on('shown.bs.modal', function() {
        // Fokusiraj prvi fokusabilni element u modalu
        const focusableElements = $modal.find('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (focusableElements.length > 0) {
          focusableElements[0].focus();
        } else {
          // Ako nema fokusabilnih elemenata, fokusiraj sam modal
          $modal.attr('tabindex', '-1').focus();
        }
      });
      
      // Vrati fokus na prethodni element kada se modal zatvori
      $modal.on('hidden.bs.modal', function() {
        if (previouslyFocusedElement) {
          previouslyFocusedElement.focus();
        }
      });
    } else {
      console.warn('Bootstrap JS nije učitan, dinamički ga učitavam...');
      
      // Učitaj Bootstrap JS dinamički
      const bootstrapScript = document.createElement('script');
      bootstrapScript.src = 'https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.bundle.min.js';
      bootstrapScript.integrity = 'sha384-Piv4xVNRyMGpqkS2by6br4gNJ7DXjqk09RmUpJ8jgGtD7zP9yug3goQfGII0yAns';
      bootstrapScript.crossOrigin = 'anonymous';
      
      bootstrapScript.onload = function() {
        console.log('Bootstrap JS je uspešno učitan');
        // Sada kada je Bootstrap učitan, prikaži modal sa poboljšanim upravljanjem fokusom
        safeShowModal(modalSelector);
      };
      
      bootstrapScript.onerror = function() {
        console.error('Greška pri učitavanju Bootstrap JS-a');
        alert('Greška pri učitavanju Bootstrap JS-a. Modal se ne može prikazati.');
      };
      
      document.head.appendChild(bootstrapScript);
    }
  } catch (e) {
    console.error('Greška pri prikazivanju modala:', e);
    alert('Greška pri prikazivanju modala: ' + e.message);
  }
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
  console.log('Opening audit day modal for event:', event);
  console.log('Event extended props:', event.extendedProps);
  
  try {
    // Prikaži modal koristeći safeShowModal funkciju
    safeShowModal('#auditDayModal');
    
    // Postavi učitavanje za sva polja
    $('#audit-day-date').text('Učitavanje...');
    $('#audit-day-is-planned').text('Učitavanje...');
    $('#audit-day-is-actual').text('Učitavanje...');
    $('#audit-day-notes').text('Učitavanje...');
    $('#audit-day-audit-id').text('Učitavanje...');
    
    // Dobavi podatke iz event objekta
    const eventProps = event.extendedProps || {};
    const eventType = eventProps.eventType;
    const auditDayId = eventProps.audit_day_id;
    const auditId = eventProps.audit_id;
    
    console.log('Event type:', eventType);
    console.log('Audit day ID from event:', auditDayId);
    console.log('Audit ID from event:', auditId);
    
    // Proveri da li je ovo zaista audit_day događaj
    if (eventType !== 'audit_day') {
      console.warn('Događaj nije tipa audit_day, ali je pozvana funkcija openAuditDayModal');
    }
    
    if (!auditId) {
      console.error('Nije pronađen ID audita u event objektu');
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
    // Prikaži modal koristeći safeShowModal funkciju
    safeShowModal('#cycleAuditModal');
    
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
    if (!window.certificationCycleJsonBaseUrl && !certificationCycleJsonBaseUrl) {
      console.error('certificationCycleJsonBaseUrl nije definisan');
      $('#cycle-start-date').text('Greška: URL nije dostupan');
      $('#cycle-end-date').text('Greška: URL nije dostupan');
      $('#cycle-cycle-status').text('Greška: URL nije dostupan');
      return;
    }
    
    // Koristi globalni window.certificationCycleJsonBaseUrl ili lokalni certificationCycleJsonBaseUrl
    const baseUrl = window.certificationCycleJsonBaseUrl || certificationCycleJsonBaseUrl;
    const ajaxUrl = `${baseUrl}${cycleId}/json/`;
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
  console.log('Opening appointment modal for event:', event);
  console.log('Event extended props:', event.extendedProps);
  
  try {
    // Prikaži modal
    $('#appointmentDetailModal').modal('show');
    
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

// Inicijalizacija kalendara kada je DOM učitan
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM učitan, inicijalizacija kalendara...');
  
  // Provera da li je jQuery dostupan
  if (typeof jQuery === 'undefined') {
    console.error('jQuery nije dostupan!');
    return;
  }
  
  // Provera da li je FullCalendar dostupan
  if (typeof FullCalendar === 'undefined') {
    console.error('FullCalendar nije dostupan!');
    return;
  }
  
  // Provera da li postoji element kalendara
  const calendarEl = document.getElementById('calendar');
  if (!calendarEl) {
    console.error('Element kalendara nije pronađen!');
    return;
  }
  
  try {
    // Inicijalizacija kalendara
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
      eventClick: function(info) {
        const eventType = info.event.extendedProps?.type;
        console.log('Event clicked:', info.event);
        console.log('Event type:', eventType);
        
        if (eventType === 'appointment') {
          openAppointmentModal(info.event);
        } else if (eventType === 'audit_day') {
          openAuditDayModal(info.event);
        } else if (eventType === 'cycle_audit') {
          openCycleAuditModal(info.event);
        }
      }
    });
    
    // Renderuj kalendar
    calendar.render();
    console.log('Kalendar uspešno inicijalizovan');
  } catch (error) {
    console.error('Greška pri inicijalizaciji kalendara:', error);
  }
});

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
      updateAppointmentDates(info.event);
    },
    eventResize: function(info) {
      updateAppointmentDates(info.event);
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
      const eventType = eventProps.eventType;
      console.log('Event type:', eventType);
      console.log('Event extended props:', eventProps);
      console.log('Event ID:', info.event.id);
      
      // Proveri da li je ID događaja u formatu koji sadrži ID audita
      let auditId = null;
      
      if (eventType === 'appointment') {
        // Open appointment modal
        const appointmentId = info.event.id.replace('appointment_', '');
        console.log('Opening appointment modal for ID:', appointmentId);
        openAppointmentDetailModal(appointmentId);
      } else if (eventType === 'cycle_audit') {
        // Open cycle audit modal
        const cycleId = eventProps.cycle_id;
        console.log('Opening cycle audit modal for cycle ID:', cycleId);
        openCycleAuditModal(info.event);
        return false;
      } else if (eventType === 'audit_day') {
        // Open audit day modal
        console.log('Opening audit day modal for event:', info.event);
        openAuditDayModal(info.event);
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
    console.log('Using URL:', auditDetailUrl.replace('0', auditId));
    
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
      url: auditDetailUrl.replace('0', auditId),
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
    console.log('updateAppointmentDates called for event:', event);
    
    // Proveri tip događaja iz extendedProps
    const eventType = event.extendedProps?.eventType;
    console.log('Event type:', eventType);
    
    // Različito procesiranje zavisno od tipa događaja
    if (eventType === 'appointment') {
      // Originalna logika za appointment događaje
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
        success: function(response) {
          console.log('Appointment date updated successfully:', response);
        },
        error: function(xhr) {
          alert('Došlo je do greške prilikom ažuriranja datuma sastanka.');
          console.error(xhr.responseText);
          calendar.refetchEvents();
        }
      });
    } else if (eventType === 'audit_day' || eventType === 'cycle_audit') {
      // Logika za audit_day i cycle_audit događaje
      // Izvuci ID iz event.id (npr. 'audit_day_planned_123' -> '123')
      let entityId;
      if (event.id.includes('_')) {
        const parts = event.id.split('_');
        entityId = parts[parts.length - 1];
      } else {
        entityId = event.id;
      }
      
      // Pripremi podatke za API
      const formData = {
        event_id: event.id,
        event_type: eventType,
        new_date: event.start.toISOString().split('T')[0], // samo datum bez vremena
        audit_id: event.extendedProps?.audit_id,
        cycle_id: event.extendedProps?.cycle_id
      };
      
      console.log('Sending update for audit/cycle event:', formData);
      
      // Koristi update_event_date API endpoint
      $.ajax({
        url: '/company/api/update-event-date/',
        method: 'POST',
        data: formData,
        headers: {
          'X-CSRFToken': getCsrfToken()
        },
        success: function(response) {
          console.log('Event date updated successfully:', response);
          // Prikaži modal za potvrdu ako je potrebno
          if (eventType === 'audit_day') {
            openAuditDayModal(event);
          } else if (eventType === 'cycle_audit') {
            openCycleAuditModal(event);
          }
        },
        error: function(xhr) {
          alert('Došlo je do greške prilikom ažuriranja datuma događaja.');
          console.error('Error updating event date:', xhr.responseText);
          calendar.refetchEvents();
        }
      });
    } else {
      console.warn('Nepoznat tip događaja:', eventType);
      alert('Nije moguće ažurirati ovaj tip događaja.');
      calendar.refetchEvents(); // Vrati događaj na originalnu poziciju
    }
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
      if (!certificationCycleJsonBaseUrl) {
        console.error('certificationCycleJsonBaseUrl nije definisan');
        $('#cycle-start-date').text('Greška: URL nije dostupan');
        $('#cycle-end-date').text('Greška: URL nije dostupan');
        $('#cycle-cycle-status').text('Greška: URL nije dostupan');
        return;
      }
      
      const ajaxUrl = certificationCycleJsonBaseUrl.replace('0', cycleId);
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
