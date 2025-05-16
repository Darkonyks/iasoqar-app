$(document).ready(function() {
  // Funkcionalnost aktiviranja taba iz URL-a ili pamćenje poslednjeg aktivnog taba
  var activeTab = sessionStorage.getItem('activeCompanyDetailTab');
  
  // Aktiviranje taba iz URL-a ako postoji hash
  var hash = window.location.hash;
  if (hash) {
    $('.nav-tabs a[href="' + hash + '"]').tab('show');
    sessionStorage.setItem('activeCompanyDetailTab', hash);
  } else if (activeTab) {
    // Ako nema hash-a u URL-u, ali je zapamćen tab u sessionStorage
    $('.nav-tabs a[href="' + activeTab + '"]').tab('show');
  }
  
  // Čuvanje aktivnog taba pri promeni
  $('.nav-tabs a').on('shown.bs.tab', function(e) {
    var currentTab = $(e.target).attr('href');
    sessionStorage.setItem('activeCompanyDetailTab', currentTab);
    
    // Ažuriranje URL-a sa hash-om za bookmark
    history.replaceState(null, null, currentTab);
  });
  
  // Tooltip inicijalizacija
  $('[data-toggle="tooltip"]').tooltip();
});
