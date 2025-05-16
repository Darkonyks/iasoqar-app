/**
 * Pomoćna debug skripta za proveru funkcionisanja tabelarnog prikaza standarda
 */

$(function() {
  console.log("DEBUG SKRIPTA JE UČITANA");
  
  // Proveri da li imamo standarde
  if (typeof window.existingStandards !== 'undefined') {
    console.log("existingStandards je definisan:", window.existingStandards);
  } else {
    console.log("existingStandards nije definisan");
  }
  
  // Direktno postavi neke test podatke u tabelu standarda
  function testStandardsTable() {
    var tableBody = $('#standards-list');
    var noStandardsMessage = $('#no-standards-message');
    
    console.log("Test pristupa tabeli standarda:");
    console.log("Tabela postoji:", tableBody.length > 0);
    console.log("Poruka za praznu tabelu postoji:", noStandardsMessage.length > 0);
    
    // Ako tabela postoji, pokušaj dodati test podatke
    if (tableBody.length > 0) {
      var testData = [
        { name: "TEST - ISO 9001:2015", issue_date: "2023-01-01", expiry_date: "2026-01-01", notes: "Test standard" }
      ];
      
      var html = '';
      for (var i = 0; i < testData.length; i++) {
        var standard = testData[i];
        html += '<tr>' +
                '<td><strong>' + standard.name + '</strong></td>' +
                '<td>' + (standard.issue_date || '-') + '</td>' +
                '<td>' + (standard.expiry_date || '-') + '</td>' +
                '<td>' + (standard.notes || '-') + '</td>' +
                '<td><button class="btn btn-sm btn-danger">X</button></td>' +
                '</tr>';
      }
      
      tableBody.html(html);
      console.log("Test podaci dodati u tabelu");
    }
  }
  
  // Proveri strukturu HTML dokumenta
  function checkHtmlStructure() {
    console.log("Standards tab element:", $('#standards').length);
    console.log("Standards table:", $('#standards table').length);
    console.log("Standards list:", $('#standards-list').length);
    
    // Probaj drugi selektor
    var altSelector = $('#standards div.tab-pane tbody');
    console.log("Alternate tbody selector found:", altSelector.length);
  }
  
  // Izvrši testove nakon kratke pauze
  setTimeout(function() {
    console.log("----------------------");
    console.log("POKRETANJE TESTOVA");
    console.log("----------------------");
    checkHtmlStructure();
    testStandardsTable();
  }, 1000);
});
