/**
 * JavaScript za funkcionalnosti forme za kompanije
 * Datoteka: company-form.js
 */

$(function() {
  // Funkcija za inicijalizaciju tabova
  function initTabs() {
    // Aktiviraj tabove
    $('#companyFormTabs a').on('click', function (e) {
      e.preventDefault();
      $(this).tab('show');
    });
    
    // Zapamti aktivni tab
    $('#companyFormTabs a').on('shown.bs.tab', function(e) {
      var activeTab = $(e.target).attr('href');
      localStorage.setItem('companyFormActiveTab', activeTab);
    });
    
    // Postavi hash u URL za bookmarkovanje
    var hash = window.location.hash;
    if (hash && $(hash).length) {
      $('#companyFormTabs a[href="' + hash + '"]').tab('show');
    }
    
    // Ažuriraj hash pri promeni taba
    $('#companyFormTabs a').on('shown.bs.tab', function(e) {
      if (history.pushState) {
        history.pushState(null, null, $(e.target).attr('href'));
      } else {
        location.hash = $(e.target).attr('href');
      }
    });
  }
  
  // Inicijalizacija tabova
  initTabs();
  
  // Validacija forme
  $('form').on('submit', function(e) {
    console.log('========== FORM SUBMISSION STARTED ==========');
    var $form = $(this);
    var requiredFields = $form.find('[required]');
    var valid = true;
    var invalidFields = [];
    
    // Validacija obaveznih polja
    requiredFields.each(function() {
      var $field = $(this);
      var fieldId = $field.attr('id') || 'unknown';
      var fieldName = $('label[for="' + fieldId + '"]').text().trim() || fieldId;
      
      if (!$field.val()) {
        $field.addClass('is-invalid');
        invalidFields.push(fieldName);
        valid = false;
        console.warn('Obavezno polje nije popunjeno:', fieldName, fieldId);
      } else {
        $field.removeClass('is-invalid');
      }
    });
    
    if (invalidFields.length > 0) {
      console.error('Neuspešna validacija forme - sledeća polja nisu popunjena:', invalidFields);
    } else {
      console.log('Validacija forme uspešna - sva obavezna polja su popunjena');
    }

    // Pripremi IAF/EAC kodove i standarde podatke pre slanja forme
    try {
      prepareIAFEACData();
      console.log('IAF/EAC podaci su uspešno pripremljeni');
    } catch (error) {
      console.error('Greška pri pripremi IAF/EAC podataka:', error);
      valid = false;
    }
    
    try {
      prepareStandardsData();
      console.log('Podaci o standardima su uspešno pripremljeni');
    } catch (error) {
      console.error('Greška pri pripremi podataka o standardima:', error);
      valid = false;
    }
    
    // Detaljno debagovanje
    console.log('Form action:', $form.attr('action'));
    console.log('Form method:', $form.attr('method'));
    console.log('CSRF token present:', $form.find('input[name="csrfmiddlewaretoken"]').length > 0);
    console.log('Standards data:', standardsData);
    console.log('Standards data JSON:', JSON.stringify(standardsData));
    console.log('Standards hidden field value:', $('#standards_data').val());
    console.log('IAF/EAC data:', iafEacCodesData);
    console.log('IAF/EAC data JSON:', JSON.stringify(iafEacCodesData));
    console.log('IAF/EAC hidden field value:', $('#iaf_eac_codes_data').val());
    
    if (valid) {
      console.log('Forma je validna, nastavlja se sa slanjem...');
    } else {
      console.error('Forma nije validna, slanje je prekinuto');
      e.preventDefault(); // Eksplicitno zaustavi slanje forme ako nije validna
    }
    
    console.log('========== FORM SUBMISSION ENDED ==========');
    return valid;
  });

  // Inicijalizacija datepicker-a za datumska polja
  $('.datepicker').datepicker({
    format: 'yyyy-mm-dd',
    autoclose: true,
    todayHighlight: true,
    language: 'sr-latin'
  });

  // =========================================================================
  // IAF/EAC KODOVI FUNKCIONALNOSTI
  // =========================================================================
  
  // Funkcionalnosti za IAF/EAC kodove
  var iafEacCodesData = [];

  // Pripremi postojeće kodove (ako postoje)
  if (typeof window.existingIAFEACCodes !== 'undefined' && window.existingIAFEACCodes && window.existingIAFEACCodes.length > 0) {
    iafEacCodesData = JSON.parse(JSON.stringify(window.existingIAFEACCodes));
    console.log('Loaded existing IAF/EAC codes:', iafEacCodesData);
  }

  // Funkcija koja priprema IAF/EAC podatke za slanje
  function prepareIAFEACData() {
    console.log('Preparing IAF/EAC data:', iafEacCodesData);
    $('#iaf_eac_codes_data').val(JSON.stringify(iafEacCodesData));
    console.log('IAF/EAC hidden field value:', $('#iaf_eac_codes_data').val());
  }

  // Inicijalno ažuriranje prikaza ako već postoje kodovi
  if (iafEacCodesData.length > 0) {
    updateIAFEACCodesDisplay();
  }

  // Dodavanje novog IAF/EAC koda
  $('#add-iaf-eac-code').on('click', function() {
    var codeSelect = $('#iaf_eac_code_select');
    var codeId = codeSelect.val();
    
    if (!codeId) {
      alert('Molimo izaberite IAF/EAC kod');
      return;
    }
    
    var codeText = codeSelect.find('option:selected').text();
    var codeParts = codeText.split(' - ');
    var codeValue = codeParts[0] || '';
    var codeDescription = codeSelect.find('option:selected').data('description') || '';
    var notes = $('#iaf_eac_code_notes').val() || '';
    var isPrimary = $('#iaf_eac_is_primary').prop('checked');
    
    // Proveri da li kod već postoji
    var codeExists = false;
    for (var i = 0; i < iafEacCodesData.length; i++) {
      if (iafEacCodesData[i].id == codeId) {
        codeExists = true;
        break;
      }
    }
    
    if (codeExists) {
      alert('Ovaj IAF/EAC kod je već dodeljen kompaniji');
      return;
    }
    
    // Ako je izabran kao primarni ili ako je prvi kod, resetuj ostale primarne kodove
    if (isPrimary || iafEacCodesData.length === 0) {
      for (var j = 0; j < iafEacCodesData.length; j++) {
        iafEacCodesData[j].is_primary = false;
      }
      isPrimary = true;
    }
    
    // Dodaj novi kod u niz
    var newCode = {
      id: codeId,
      code: codeValue,
      description: codeDescription,
      is_primary: isPrimary,
      notes: notes,
      is_new: true
    };
    
    iafEacCodesData.push(newCode);
    
    // Ažuriraj prikaz
    updateIAFEACCodesDisplay();
    
    // Resetuj polja za unos
    codeSelect.val('');
    $('#iaf_eac_code_notes').val('');
    $('#iaf_eac_is_primary').prop('checked', false);
  });
  
  // Postavljanje koda kao primarnog
  $(document).on('click', '.btn-make-primary', function() {
    var codeId = $(this).data('id');
    var codeIndex = -1;
    
    // Resetuj sve postojeće primarne kodove
    for (var i = 0; i < iafEacCodesData.length; i++) {
      if (iafEacCodesData[i].relation_id == codeId) {
        codeIndex = i;
      }
      iafEacCodesData[i].is_primary = false;
    }
    
    // Postavi izabrani kod kao primarni
    if (codeIndex >= 0) {
      iafEacCodesData[codeIndex].is_primary = true;
    }
    
    // Ažuriraj prikaz
    updateIAFEACCodesDisplay();
  });
  
  // Uklanjanje koda
  $(document).on('click', '.btn-remove-iaf-code', function() {
    var codeId = $(this).data('id');
    var wasPrimary = false;
    var newIafEacCodesData = [];
    
    // Pronađi i ukloni kod iz niza
    for (var i = 0; i < iafEacCodesData.length; i++) {
      if (iafEacCodesData[i].relation_id == codeId) {
        wasPrimary = iafEacCodesData[i].is_primary;
      } else {
        newIafEacCodesData.push(iafEacCodesData[i]);
      }
    }
    
    // Ažuriraj glavni niz
    iafEacCodesData = newIafEacCodesData;
    
    // Ako je uklonjeni kod bio primarni, postavi prvi preostali kod kao primarni
    if (wasPrimary && iafEacCodesData.length > 0) {
      iafEacCodesData[0].is_primary = true;
    }
    
    // Ažuriraj prikaz
    updateIAFEACCodesDisplay();
  });
  
  // Funkcija za ažuriranje prikaza IAF/EAC kodova
  function updateIAFEACCodesDisplay() {
    var tableContainer = $('#iaf-eac-codes-list');
    var noCodesMessage = $('#no-iaf-codes-message');
    
    if (iafEacCodesData.length === 0) {
      tableContainer.html('');
      if (noCodesMessage.length) {
        noCodesMessage.show();
      }
      return;
    }
    
    if (noCodesMessage.length) {
      noCodesMessage.hide();
    }
    
    var html = '';
    
    for (var i = 0; i < iafEacCodesData.length; i++) {
      var item = iafEacCodesData[i];
      var rowId = item.relation_id ? 'iaf-eac-code-' + item.relation_id : 'new-iaf-eac-code-' + item.id;
      var primaryBadge = item.is_primary ? 
        '<span class="badge badge-primary">Primarni kod</span>' : 
        '<span class="badge badge-secondary">Sekundarni kod</span>';
      
      var actionButtons = '<div class="btn-group btn-group-sm">';
      
      if (!item.is_primary) {
        var dataId = item.relation_id || 'new-' + item.id;
        actionButtons += '<button type="button" class="btn btn-outline-primary btn-make-primary" data-id="' + dataId + '">' +
                        '<i class="fas fa-star"></i></button>';
      }
      
      actionButtons += '<button type="button" class="btn btn-outline-danger btn-remove-iaf-code" data-id="' + 
                        (item.relation_id || 'new-' + item.id) + '">' +
                        '<i class="fas fa-trash"></i></button>';
      actionButtons += '</div>';
      
      html += '<tr id="' + rowId + '">' +
              '<td><strong>' + (item.code || '') + '</strong></td>' +
              '<td>' + (item.description || '') + '</td>' +
              '<td>' + primaryBadge + '</td>' +
              '<td>' + (item.notes || '-') + '</td>' +
              '<td>' + actionButtons + '</td>' +
              '</tr>';
    }
    
    tableContainer.html(html);
  }

  // =========================================================================
  // STANDARDI FUNKCIONALNOSTI
  // =========================================================================
  
  // Funkcionalnosti za standarde
  var standardsData = [];
  
  // Inicijalizuj standardsData sa postojećim standardima (ako postoje)
  if (typeof window.existingStandards !== 'undefined' && window.existingStandards && window.existingStandards.length > 0) {
    standardsData = JSON.parse(JSON.stringify(window.existingStandards));
    console.log('Loaded existing standards:', standardsData);
  }
  
  // Funkcija koja priprema podatke o standardima za slanje
  function prepareStandardsData() {
    console.log('Preparing standards data:', standardsData);
    
    // Dodatna provera i logovanje
    if (standardsData.length === 0) {
      console.warn('standardsData je prazan niz - ovo je ok samo ako nema standarda');
    }
    
    // Proveri da li ima praznih ID polja
    for (var i = 0; i < standardsData.length; i++) {
      if (!standardsData[i].id) {
        console.error('Standard na poziciji ' + i + ' nema ID!');
      }
    }
    
    // Postavi vrednost u hidden polje
    $('#standards_data').val(JSON.stringify(standardsData));
    console.log('Standards hidden field value:', $('#standards_data').val());
    
    // Proveri da li je hidden polje zaista postavljeno
    if (!$('#standards_data').val()) {
      console.error('Hidden field #standards_data je prazan nakon postavljanja!');  
    }
  }
  
  // Inicijalno ažuriranje prikaza standarda ako već postoje
  $(document).ready(function() {
    // Sačekaj da se DOM u potpunosti učita pre renderovanja tabele
    console.log('Document ready, initializing standards table');
    console.log('Initial standardsData:', standardsData);
    
    // Osiguraj da imamo ID elementa za tabelu
    if ($('#standards-list').length === 0) {
      console.warn('standards-list not found, check if element exists in HTML');
    }
    
    // Pokušaj renderovati tabelu bez obzira da li ima podataka ili ne
    // ovo će pravilno postaviti i poruku o nedostatku standarda
    renderStandardsTable();
    
    // Inicijalizuj funkcionalnost za brisanje standarda
    setupStandardRemoveButtons();
    
    // Prošireni debug za proveravanje HTML strukture
    console.log('Standards tab HTML structure:', $('#standards').html());
  });
  
  // Dodaj event handler za dugme za dodavanje standarda
  $('#add-standard').on('click', function() {
    addStandard();
  });
  
  // Čuvanje indeksa standarda koji se briše
  var currentStandardIndexToDelete = -1;
  
  // Inicijalno podesi funkcije za brisanje standarda
  function setupStandardRemoveButtons() {
    // Event listener za klik na dugme za brisanje standarda
    $('#standards-list').on('click', '.btn-remove-standard', function() {
      var index = $(this).data('index');
      console.log('Standard requested for deletion at index:', index);
      
      if (index !== undefined && index >= 0 && index < standardsData.length) {
        // Sačuvaj indeks za kasnije korišćenje
        currentStandardIndexToDelete = index;
        
        // Prikaži ime standarda u modalnom dijalogu
        var standardName = standardsData[index].name || 'Nepoznat standard';
        $('#standardToDeleteName').text(standardName);
        
        // Prikaži modalni dijalog za potvrdu
        $('#deleteStandardModal').modal('show');
      } else {
        console.error('Invalid standard index:', index);
      }
    });
    
    // Event listener za potvrdu brisanja standarda
    $('#confirmDeleteStandard').on('click', function() {
      console.log('Confirmed deletion of standard at index:', currentStandardIndexToDelete);
      
      if (currentStandardIndexToDelete >= 0 && currentStandardIndexToDelete < standardsData.length) {
        // Ukloni standard iz niza podataka
        standardsData.splice(currentStandardIndexToDelete, 1);
        
        // Osvežavanje prikaza tabele
        console.log('Rerendering standards table after confirmed removal');
        renderStandardsTable();
        
        // Ako nema više standarda, prikaži poruku
        if (standardsData.length === 0) {
          $('#no-standards-message').show();
        }
        
        // Resetuj indeks
        currentStandardIndexToDelete = -1;
        
        // Zatvori modalni dijalog
        $('#deleteStandardModal').modal('hide');
      } else {
        console.error('Invalid standard index for deletion:', currentStandardIndexToDelete);
      }
    });
  }
  
  // Funkcija za prikaz standarda u tabeli - koristimo samo ovu funkciju za konzistentnost
  function renderStandardsTable() {
    // Prošireni debug za praćenje problema
    console.log('Rendering standards table - standardsData:', standardsData);
    
    // Osiguraj da prvo nađemo pravi container
    var tableContainer = $('#standards-list');
    console.log('Standards list container found:', tableContainer.length > 0);
    
    // Ako ne možemo naći container, pokušaj ponovo sa punom putanjom
    if (tableContainer.length === 0) {
      console.warn('Container #standards-list not found, trying alternative selector');
      tableContainer = $('#standards div.tab-pane tbody');
      console.log('Alternative selector found:', tableContainer.length > 0);
      
      // Ako i dalje ne možemo naći, prikaži upozorenje i prekini
      if (tableContainer.length === 0) {
        console.error('Cannot find standards table container');
        return;
      }
    }
    
    var noStandardsMessage = $('#no-standards-message');
    
    // Ako nema standarda, prikaži poruku
    if (!standardsData || standardsData.length === 0) {
      console.log('No standards data to display');
      tableContainer.html('');
      if (noStandardsMessage.length) {
        noStandardsMessage.show();
      }
      return;
    }
    
    if (noStandardsMessage.length) {
      noStandardsMessage.hide();
    }
    
    var html = '';
    
    // Generiši HTML za svaki standard
    for (var i = 0; i < standardsData.length; i++) {
      var standard = standardsData[i];
      console.log('Processing standard:', standard);
      
      var rowId = standard.standard_id ? 'standard-' + standard.standard_id : 'new-standard-' + standard.id;
      
      // Osiguraj da ime standarda postoji
      var standardName = standard.name || 'Nepoznat standard';
      console.log('Standard name:', standardName);
      
      // Formatiraj datume
      var formattedIssueDate = standard.issue_date ? formatDateDisplay(standard.issue_date) : '-';
      var formattedExpiryDate = standard.expiry_date ? formatDateDisplay(standard.expiry_date) : '-';
      
      // Dugme za uklanjanje standarda
      var actionButtons = '<div class="btn-group btn-group-sm">' +
        '<button type="button" class="btn btn-outline-danger btn-remove-standard" data-index="' + i + '">' +
        '<i class="fas fa-trash"></i></button>' +
        '</div>';
      
      // Generiši HTML za red tabele
      html += '<tr id="' + rowId + '">' +
              '<td><strong>' + standardName + '</strong></td>' +
              '<td>' + formattedIssueDate + '</td>' +
              '<td>' + formattedExpiryDate + '</td>' +
              '<td>' + (standard.notes || '-') + '</td>' +
              '<td>' + actionButtons + '</td>' +
              '</tr>';
    }
    
    // Prikaži HTML u tabeli
    console.log('Setting table HTML:', html);
    tableContainer.html(html);
    
    // Proveri da li je HTML zaista postavljen
    console.log('Table HTML after update:', tableContainer.html());
  }
  
  // Funkcija za dodavanje novog standarda
  function addStandard() {
    var standardId = $('#standard_definition_select').val();
    var standardText = $('#standard_definition_select option:selected').text().trim();
    var issueDate = $('#standard_issue_date').val();
    var expiryDate = $('#standard_expiry_date').val();
    var notes = $('#standard_notes').val();
    
    if (!standardId) {
      alert('Molimo izaberite standard');
      return;
    }
    
    // Proveri da li standard već postoji u listi
    for (var i = 0; i < standardsData.length; i++) {
      if (standardsData[i].id == standardId) {
        alert('Ovaj standard je već dodat');
        return;
      }
    }
    
    // Kreiraj objekat novog standarda za slanje na server
    var newStandard = {
      id: standardId,
      name: standardText,
      issue_date: issueDate,
      expiry_date: expiryDate,
      notes: notes,
      standard_id: null // novi standard nema ID dok se ne sačuva
    };
    
    // Dodaj novi standard u niz podataka
    standardsData.push(newStandard);
    
    // Formatiraj datume za prikaz
    var formattedIssueDate = issueDate ? formatDateDisplay(issueDate) : '-';
    var formattedExpiryDate = expiryDate ? formatDateDisplay(expiryDate) : '-';
    
    // Kreiraj novi red u tabeli za novi standard - direktno dodaj HTML
    var newRowId = 'new-standard-' + standardId;
    var newRowHtml = '<tr id="' + newRowId + '">' +
                    '<td><strong>' + standardText + '</strong></td>' +
                    '<td>' + formattedIssueDate + '</td>' +
                    '<td>' + formattedExpiryDate + '</td>' +
                    '<td>' + (notes || '-') + '</td>' +
                    '<td><div class="btn-group btn-group-sm">' +
                    '<button type="button" class="btn btn-outline-danger btn-remove-standard" data-index="' + (standardsData.length - 1) + '">' +
                    '<i class="fas fa-trash"></i></button></div></td>' +
                    '</tr>';
    
    // Dodaj novi red u tabelu
    $('#standards-list').append(newRowHtml);
    
    // Sakrij poruku o nedostatku standarda ako postoji
    $('#no-standards-message').hide();
    
    // Očisti polja forme
    $('#standard_definition_select').val('');
    $('#standard_issue_date').val('');
    $('#standard_expiry_date').val('');
    $('#standard_notes').val('');
  }
  
  // Pomoćna funkcija za formatiranje datuma u lepši prikaz
  function formatDateDisplay(dateString) {
    console.log('Formatting date:', dateString);
    
    if (!dateString) return '-';
    if (dateString === '') return '-';
    
    try {
      // Pokušaj formatirati datum
      var parts = dateString.split('-');
      console.log('Date parts:', parts);
      
      if (parts.length === 3) {
        var formattedDate = parts[2] + '.' + parts[1] + '.' + parts[0] + '.';
        console.log('Formatted date:', formattedDate);
        return formattedDate;
      }
    } catch (e) {
      console.error('Error formatting date:', e);
    }
    
    return dateString;
  }
  
  // =========================================================================
  // OBAVEZNA POLJA FUNKCIONALNOSTI
  // =========================================================================
  
  // Funkcionalnost za prikaz i navigaciju obaveznih polja
  $('#showRequiredFieldsBtn').on('click', function() {
    updateRequiredFieldsList();
    $('#requiredFieldsModal').modal('show');
  });
  
  // Funkcija za proveru i prikaz obaveznih polja koja nisu popunjena
  function updateRequiredFieldsList() {
    var requiredFields = [];
    
    // Pronađi sva polja koja su obavezna i nisu popunjena
    $('input[required], select[required], textarea[required]').each(function() {
      var $field = $(this);
      
      if (!$field.val()) {
        // Dobavi informacije o polju
        var fieldId = $field.attr('id');
        var fieldName = $('label[for="' + fieldId + '"]').text().trim();
        var tabId = $field.closest('.tab-pane').attr('id');
        var tabName = $('a[href="#' + tabId + '"]').text().trim();
        
        requiredFields.push({
          id: fieldId,
          name: fieldName,
          tabId: tabId,
          tabName: tabName
        });
      }
    });
    
    // Pripremi HTML za listu obaveznih polja
    var $requiredFieldsList = $('#requiredFieldsList');
    $requiredFieldsList.empty();
    
    if (requiredFields.length === 0) {
      $requiredFieldsList.html('<div class="alert alert-success"><i class="fas fa-check-circle"></i> Sva obavezna polja su popunjena.</div>');
      return;
    }
    
    // Grupiši polja po tabu
    var fieldsByTab = {};
    requiredFields.forEach(function(field) {
      if (!fieldsByTab[field.tabId]) {
        fieldsByTab[field.tabId] = {
          tabName: field.tabName,
          fields: []
        };
      }
      fieldsByTab[field.tabId].fields.push(field);
    });
    
    // Kreiraj HTML za svaku grupu
    Object.keys(fieldsByTab).forEach(function(tabId) {
      var tabGroup = fieldsByTab[tabId];
      
      var $tabHeader = $('<div class="list-group-item list-group-item-action active">' + 
                        '<i class="fas fa-folder"></i> ' + tabGroup.tabName + ' (' + tabGroup.fields.length + ' polja)' +
                        '</div>');
      
      $requiredFieldsList.append($tabHeader);
      
      tabGroup.fields.forEach(function(field) {
        var $fieldItem = $('<a href="#' + field.tabId + '" class="list-group-item list-group-item-action required-field-item" ' +
                         'data-field-id="' + field.id + '" data-tab="' + field.tabId + '">' +
                         '<i class="fas fa-exclamation-circle text-danger"></i> ' + field.name +
                         '</a>');
        $requiredFieldsList.append($fieldItem);
      });
    });
    
    // Postavi event handler za klik na stavku iz liste
    $('.required-field-item').on('click', function() {
      var $this = $(this);
      var fieldId = $this.data('field-id');
      var tabId = $this.data('tab');
      
      // Zatvori modal
      $('#requiredFieldsModal').modal('hide');
      
      // Aktiviraj odgovarajući tab
      $('#companyFormTabs a[href="#' + tabId + '"]').tab('show');
      
      // Fokusiraj polje nakon kratke pauze (da bi se tab učitao)
      setTimeout(function() {
        $('#' + fieldId).focus();
        // Dodaj blink efekat
        $('#' + fieldId).addClass('highlight-field');
        setTimeout(function() {
          $('#' + fieldId).removeClass('highlight-field');
        }, 2000);
      }, 300);
    });
  }
  
  // Dodavanje CSS-a za blink efekat
  $('<style>\n' +
    '@keyframes highlight {\n' +
    '  0% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.8); }\n' +
    '  70% { box-shadow: 0 0 0 10px rgba(255, 193, 7, 0); }\n' +
    '  100% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0); }\n' +
    '}\n' +
    '.highlight-field {\n' +
    '  animation: highlight 1.5s ease-in-out 2;\n' +
    '  border-color: #ffc107;\n' +
    '}\n' +
    '</style>').appendTo('head');
});
