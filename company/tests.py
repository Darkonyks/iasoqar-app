from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, datetime
import json

from company.models import Company
from company.cycle_models import CertificationCycle, CycleAudit, AuditorReservation
from company.auditor_models import Auditor


class UpdateEventDateConflictTests(TestCase):
    def setUp(self):
        # Auth
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='pass1234')
        self.client = Client()
        self.client.login(username='tester', password='pass1234')

        # Common data
        self.company_a = Company.objects.create(name='Comp A')
        self.company_b = Company.objects.create(name='Comp B')

        self.auditor = Auditor.objects.create(
            ime_prezime='Auditor X', email='x@example.com', telefon='123'
        )

        # Base dates
        self.d1 = date(2025, 8, 14)
        self.d2 = date(2025, 8, 15)
        self.d3 = date(2025, 8, 17)

    def _create_cycle_with_initial_audit(self, company, planned_date, lead=None):
        cycle = CertificationCycle.objects.create(
            company=company,
            planirani_datum=planned_date,
            status='active',
            inicijalni_broj_dana=1,  # 1-day audit for simpler assertions
        )
        audit = CycleAudit.objects.create(
            certification_cycle=cycle,
            audit_type='initial',
            audit_status='planned',
            planned_date=planned_date,
            lead_auditor=lead,
        )
        return cycle, audit

    def _post_update(self, event_type, event_id, new_date):
        # Build ISO datetime string (naive is fine; the view normalizes it)
        iso = datetime.combine(new_date, datetime.min.time()).isoformat()
        url = reverse('company:update_event_date')
        payload = {
            'eventType': event_type,
            'eventId': event_id,
            'newDate': iso,
        }
        return self.client.post(url, data=json.dumps(payload), content_type='application/json')

    def test_cycle_audit_drag_conflict_returns_409_and_keeps_original_date(self):
        # Given audit A (Comp A) and audit B (Comp B) with SAME lead auditor
        _, audit_a = self._create_cycle_with_initial_audit(self.company_a, self.d1, self.auditor)
        _, audit_b = self._create_cycle_with_initial_audit(self.company_b, self.d2, self.auditor)

        # Sanity: A has reservation on d1; B has reservation on d2 (created in CycleAudit.save -> sync)
        self.assertTrue(AuditorReservation.objects.filter(auditor=self.auditor, date=self.d1, audit=audit_a).exists())
        self.assertTrue(AuditorReservation.objects.filter(auditor=self.auditor, date=self.d2, audit=audit_b).exists())

        # When trying to move audit A to d2 (where the auditor already works on Comp B)
        resp = self._post_update('cycle_audit', audit_a.id, self.d2)

        # Then: conflict
        self.assertEqual(resp.status_code, 409)
        self.assertIn('Nemoguće pomeriti audit', resp.json().get('error', ''))

        # And planned_date unchanged
        audit_a.refresh_from_db()
        self.assertEqual(audit_a.planned_date, self.d1)

        # And reservations for A not altered to conflicting date
        self.assertFalse(AuditorReservation.objects.filter(auditor=self.auditor, date=self.d2, audit=audit_a).exists())
        # Original reservation remains
        self.assertTrue(AuditorReservation.objects.filter(auditor=self.auditor, date=self.d1, audit=audit_a).exists())

    def test_cycle_audit_drag_success_updates_date_and_reservations(self):
        # No conflicts on d3
        _, audit_a = self._create_cycle_with_initial_audit(self.company_a, self.d1, self.auditor)

        resp = self._post_update('cycle_audit', audit_a.id, self.d3)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get('success'))

        # planned_date updated
        audit_a.refresh_from_db()
        self.assertEqual(audit_a.planned_date, self.d3)

        # Reservation moved to d3
        self.assertTrue(AuditorReservation.objects.filter(auditor=self.auditor, date=self.d3, audit=audit_a).exists())
        self.assertFalse(AuditorReservation.objects.filter(auditor=self.auditor, date=self.d1, audit=audit_a).exists())

    def test_audit_day_drag_conflict_returns_409(self):
        # Two audits with same auditor on different dates
        _, audit_a = self._create_cycle_with_initial_audit(self.company_a, self.d1, self.auditor)
        _, audit_b = self._create_cycle_with_initial_audit(self.company_b, self.d2, self.auditor)

        # Move A's audit day to B's date -> should conflict
        audit_day_a = audit_a.audit_days.first()
        self.assertIsNotNone(audit_day_a)

        resp = self._post_update('audit_day', audit_day_a.id, self.d2)
        self.assertEqual(resp.status_code, 409)
        self.assertIn('konflikta rezervacija', resp.json().get('error', '').lower())
