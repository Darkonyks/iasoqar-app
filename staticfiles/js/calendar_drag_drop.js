/**
 * ISOQAR Calendar Drag-and-Drop
 * JavaScript funkcije za podršku drag-and-drop funkcionalnosti u kalendaru
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

// Funkcija safeShowModal je definisana u calendar.js fajlu
// Ovde je uklonjena duplikat implementacija da bi se izbegli konflikti

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
    url: '/company/api/events/update-date/',
    type: 'POST',
    data: {
      type: eventType,
      id: eventId,
      date: formattedDate
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

// Inicijalizacija drag-and-drop funkcionalnosti
document.addEventListener('DOMContentLoaded', function() {
  console.log('Inicijalizacija drag-and-drop funkcionalnosti za kalendar...');
  
  // Proveri da li je kalendar već inicijalizovan
  const checkCalendarInterval = setInterval(function() {
    const calendarEl = document.getElementById('calendar');
    if (calendarEl && calendarEl._calendar) {
      clearInterval(checkCalendarInterval);
      
      try {
        const calendarApi = calendarEl._calendar.getApi();
        
        // Omogući drag-and-drop
        calendarApi.setOption('editable', true);
        
        // Dodaj eventDrop handler
        calendarApi.setOption('eventDrop', function(info) {
          const event = info.event;
          const eventType = event.extendedProps?.type || event.extendedProps?.eventType;
          let eventId;
          
          console.log('Događaj je prebačen:', event);
          console.log('Tip događaja:', eventType);
          
          // Dobavljanje ID-a događaja u zavisnosti od tipa
          if (eventType === 'audit_day') {
            eventId = event.extendedProps?.audit_day_id || event.extendedProps?.id || event.id;
          } else if (eventType === 'cycle_audit') {
            eventId = event.extendedProps?.cycle_audit_id || event.extendedProps?.id || event.id;
          } else if (eventType === 'appointment') {
            eventId = event.extendedProps?.appointment_id || event.extendedProps?.id || event.id;
          } else {
            console.error('Nepoznat tip događaja:', eventType);
            info.revert();
            return;
          }
          
          console.log('ID događaja:', eventId);
          
          if (!eventId) {
            console.error('Nije pronađen ID događaja');
            info.revert();
            return;
          }
          
          const newDate = event.start;
          
          // Prikaži modal za potvrdu promene datuma
          showDateChangeConfirmationModal(event, newDate, function(confirmed) {
            if (confirmed) {
              // Ažuriraj datum događaja na serveru
              updateEventDate(eventType, eventId, newDate);
            } else {
              // Vrati događaj na originalnu poziciju
              info.revert();
            }
          });
        });
        
        console.log('Drag-and-drop funkcionalnost uspešno inicijalizovana!');
      } catch (error) {
        console.error('Greška prilikom inicijalizacije drag-and-drop funkcionalnosti:', error);
      }
    }
  }, 500);
  
  // Prekini proveru nakon 10 sekundi ako kalendar nije pronađen
  setTimeout(function() {
    clearInterval(checkCalendarInterval);
  }, 10000);
});
