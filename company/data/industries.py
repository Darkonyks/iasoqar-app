"""
This module contains the choices for industries based on international standard industrial classification.
"""

from django.utils.translation import gettext_lazy as _

INDUSTRY_CHOICES = [
    ('agriculture', _('Poljoprivreda, šumarstvo i ribarstvo')),
    ('mining', _('Rudarstvo')),
    ('manufacturing', _('Prerađivačka industrija')),
    ('energy', _('Snabdevanje električnom energijom, gasom i parom')),
    ('water_supply', _('Snabdevanje vodom i upravljanje otpadnim vodama')),
    ('construction', _('Građevinarstvo')),
    ('geodetic', _('Geodetske usluge')),
    ('trade', _('Trgovina na veliko i malo')),
    ('transportation', _('Saobraćaj i skladištenje')),
    ('tourism', _('Turizam i turističke usluge')),
    ('hospitality', _('Usluge smeštaja i ishrane')),
    ('information', _('Informisanje i komunikacije')),
    ('it_services', _('IT usluge i razvoj softvera')),
    ('finance', _('Finansijske delatnosti i osiguranje')),
    ('real_estate', _('Poslovanje nekretninama')),
    ('professional', _('Stručne, naučne i tehničke delatnosti')),
    ('administrative', _('Administrativne i pomoćne uslužne delatnosti')),
    ('public_admin', _('Državna uprava i odbrana')),
    ('education', _('Obrazovanje')),
    ('healthcare', _('Zdravstvena i socijalna zaštita')),
    ('arts', _('Umetnost, zabava i rekreacija')),
    ('other_services', _('Ostale uslužne delatnosti')),
    ('legal_services', _('Pravne usluge')),
    ('consulting', _('Konsalting usluge')),
    ('marketing', _('Marketing i oglašavanje')),
    ('households', _('Delatnost domaćinstva kao poslodavca')),
    ('extraterritorial', _('Delatnost eksteritorijalnih organizacija i tela')),
]
