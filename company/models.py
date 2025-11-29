# Main models.py file that imports all models from separate files

# Import company models
from .company_models import (
    Company,
    KontaktOsoba,
    OstalaLokacija,
)

# Import IAF models
from .iaf_models import (
    IAFScopeReference,
    IAFEACCode,
    CompanyIAFEACCode,
)

# Import standard models
from .standard_models import (
    StandardDefinition,
    CompanyStandard,
    Standard,  # Alias za CompanyStandard za kompatibilnost
    StandardIAFScopeReference,
)

# Import auditor models
from .auditor_models import (
    Auditor,
    AuditorStandard,
    AuditorStandardIAFEACCode,
)

# Import calendar and appointment models
from .calendar_models import (
    CalendarEvent,
    Appointment,
)

# Import certification cycle models
from .cycle_models import (
    CertificationCycle,
    CycleStandard,
    CycleAudit,
    AuditorReservation,
)

# Import Srbija Tim models
from .srbija_tim_models import (
    SrbijaTim,
)

# Import Certificate models
from .certificate_models import (
    Certificate,
)
