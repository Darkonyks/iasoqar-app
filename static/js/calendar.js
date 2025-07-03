document.addEventListener('DOMContentLoaded', function() {
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
      } else if (eventType === 'audit_day' || eventType === 'cycle_audit') {
        // Open audit detail modal
        auditId = eventProps.audit_id;
        console.log('Opening audit detail modal for ID from props:', auditId);
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
      
      // Add audit status for audit events
      if (extendedProps.eventType === 'audit' && extendedProps.auditStatus) {
        const statusText = extendedProps.auditStatus === 'completed' ? 'Održana' : 'Planirana';
        tooltipContent += `<strong>Status audita:</strong> ${statusText}<br>`;
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

  // Helper functions
  function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    
    return `${day}.${month}.${year}.`;
  }
  
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
});
