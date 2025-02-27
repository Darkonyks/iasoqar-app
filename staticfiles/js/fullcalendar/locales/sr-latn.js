FullCalendar.globalLocales.push(function () {
  'use strict';

  var srLatn = {
    code: 'sr-latn',
    week: {
      dow: 1, // Monday is the first day of the week
      doy: 7  // The week that contains Jan 1st is the first week of the year
    },
    buttonText: {
      prev: 'Prethodna',
      next: 'Sledeća',
      today: 'Danas',
      month: 'Mesec',
      week: 'Nedelja',
      day: 'Dan',
      list: 'Lista'
    },
    weekText: 'Sed',
    allDayText: 'Ceo dan',
    moreLinkText: function(n) {
      return '+ još ' + n;
    },
    noEventsText: 'Nema događaja za prikaz'
  };

  return srLatn;

}());
