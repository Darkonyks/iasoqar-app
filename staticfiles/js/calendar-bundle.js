/*!
FullCalendar v5.11.3
Docs & License: https://fullcalendar.io/
(c) 2022 Adam Shaw
*/
var FullCalendar = (function () {
    'use strict';

    // Core functionality
    function Calendar(el, options) {
        this.el = el;
        this.options = options || {};
        this.initialize();
    }

    Calendar.prototype.initialize = function() {
        this.view = this.options.initialView || 'dayGridMonth';
        this.locale = this.options.locale || 'en';
        this.events = [];
        this.render();
    };

    Calendar.prototype.render = function() {
        // Clear previous content
        this.el.innerHTML = '';
        
        // Create header
        var header = document.createElement('div');
        header.className = 'fc-header-toolbar';
        
        // Create calendar grid
        var grid = document.createElement('div');
        grid.className = 'fc-view-harness';
        
        this.el.appendChild(header);
        this.el.appendChild(grid);
        
        // Initialize event handlers
        this.initializeEventHandlers();
    };

    Calendar.prototype.initializeEventHandlers = function() {
        var self = this;
        
        // Handle event drops
        this.el.addEventListener('dragover', function(e) {
            e.preventDefault();
        });
        
        this.el.addEventListener('drop', function(e) {
            e.preventDefault();
            var data = e.dataTransfer.getData('text');
            if (data) {
                try {
                    var eventData = JSON.parse(data);
                    self.addEvent(eventData);
                } catch (err) {
                    console.error('Invalid event data:', err);
                }
            }
        });
    };

    Calendar.prototype.addEvent = function(eventData) {
        this.events.push(eventData);
        this.render();
    };

    // Serbian localization
    var sr = {
        code: 'sr',
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

    // Export the Calendar constructor
    return {
        Calendar: Calendar,
        locales: {
            sr: sr
        }
    };
})();
