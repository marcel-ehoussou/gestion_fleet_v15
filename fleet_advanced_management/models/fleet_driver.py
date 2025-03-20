from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class FleetDriver(models.Model):
    _name = 'fleet.driver'
    _description = 'Conducteur de flotte'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ############################
    # Informations de base
    ############################
    name = fields.Char(string='Nom', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employé associé')
    
    # Champs image
    image_1920 = fields.Image(string='Image')
    image_128 = fields.Image(string='Image 128', related='image_1920', max_width=128, max_height=128, store=True)
    
    ############################
    # Informations sur le permis
    ############################
    license_number = fields.Char(string='Numéro de permis', required=True, tracking=True)
    license_type = fields.Selection([
        ('a', 'Type A'),
        ('b', 'Type B'),
        ('c', 'Type C'),
        ('d', 'Type D'),
    ], string='Type de permis', required=True)
    license_expiry = fields.Date(string="Date d'expiration du permis", required=True)
    
    ############################
    # Coordonnées
    ############################
    phone = fields.Char(string='Téléphone')
    email = fields.Char(string='Email')
    address = fields.Text(string='Adresse')
    
    ############################
    # Statut et disponibilité
    ############################
    state = fields.Selection([
        ('available', 'Disponible'),
        ('driving', 'En conduite'),
        ('off_duty', 'Hors service'),
        ('leave', 'En congé'),
    ], string='Statut', default='available', tracking=True)
    
    ############################
    # Affectations & Planning
    ############################
    current_vehicle_id = fields.Many2one('fleet.vehicle', string='Véhicule actuel',
                                           compute='_compute_current_vehicle', store=True)
    reservation_ids = fields.One2many('fleet.vehicle.reservation', 'driver_id', string='Réservations de véhicules')
    schedule_ids = fields.One2many('fleet.driver.schedule', 'driver_id', string='Planning de travail')
    schedule_count = fields.Integer(string='Nombre de plannings', compute='_compute_schedule_count', store=True)
    
    ############################
    # Indicateurs de performance
    ############################
    total_distance = fields.Float(string='Distance totale parcourue',
                                  compute='_compute_total_distance', store=True)
    fuel_efficiency_rating = fields.Float(string='Efficacité énergétique',
                                          compute='_compute_efficiency_rating', store=True)
    accident_count = fields.Integer(string='Nombre d\'accidents',
                                    compute='_compute_accident_count', store=True)
    performance_score = fields.Float(string='Score de performance',
                                     compute='_compute_performance_score', store=True)
    
    ############################
    # Aspects financiers
    ############################
    revenue_generated = fields.Float(string='Revenu total généré',
                                     compute='_compute_revenue', store=True)
    
    ############################
    # Documents liés
    ############################
    document_ids = fields.One2many('fleet.driver.document', 'driver_id', string='Documents')
    
    #################################
    # Méthodes de calcul (compute)
    #################################
    @api.depends('reservation_ids')
    def _compute_current_vehicle(self):
        for driver in self:
            current_reservation = driver.reservation_ids.filtered(lambda r: r.state == 'ongoing')
            driver.current_vehicle_id = current_reservation and current_reservation[0].vehicle_id or False

    @api.depends('reservation_ids.state', 'reservation_ids.final_odometer', 'reservation_ids.initial_odometer', 'reservation_ids.actual_distance')
    def _compute_total_distance(self):
        for driver in self:
            total = 0.0
            # Additionne la actual_distance fournie directement par chaque réservation (si définie)
            for reservation in driver.reservation_ids:
                total += getattr(reservation, 'actual_distance', 0.0)
            # Pour les réservations terminées, on peut utiliser les relevés d'odomètre
            completed_reservations = driver.reservation_ids.filtered(lambda r: r.state == 'done')
            for reservation in completed_reservations:
                if reservation.final_odometer and reservation.initial_odometer:
                    total += (reservation.final_odometer - reservation.initial_odometer)
            driver.total_distance = total
            

    @api.depends('reservation_ids.state', 'reservation_ids.actual_fuel_cost', 'reservation_ids.estimated_distance')
    def _compute_efficiency_rating(self):
        for driver in self:
            total_consumption = 0.0
            total_distance = 0.0
            completed_reservations = driver.reservation_ids.filtered(lambda r: r.state == 'done')
            for reservation in completed_reservations:
                if reservation.actual_fuel_cost and reservation.estimated_distance:
                    total_consumption += reservation.actual_fuel_cost
                    total_distance += reservation.estimated_distance
            driver.fuel_efficiency_rating = (total_distance / total_consumption) if total_consumption else 0.0

    @api.depends('reservation_ids.state', 'reservation_ids.accident_count')
    def _compute_accident_count(self):
        for driver in self:
            total_accidents = 0
            completed_reservations = driver.reservation_ids.filtered(lambda r: r.state == 'done')
            for reservation in completed_reservations:
                if reservation.accident_count:
                    total_accidents += reservation.accident_count
            driver.accident_count = total_accidents

    @api.depends('reservation_ids.state', 'reservation_ids.total_cost')
    def _compute_revenue(self):
        for driver in self:
            total_revenue = 0.0
            completed_reservations = driver.reservation_ids.filtered(lambda r: r.state == 'done')
            for reservation in completed_reservations:
                if reservation.total_cost:
                    total_revenue += reservation.total_cost
            driver.revenue_generated = total_revenue

    @api.depends('total_distance', 'fuel_efficiency_rating', 'accident_count', 'revenue_generated')
    def _compute_performance_score(self):
        for driver in self:
            score = 100.0
            score -= driver.accident_count * 10
            if driver.fuel_efficiency_rating:
                score += min(driver.fuel_efficiency_rating * 2, 20)
            if driver.total_distance:
                score += min(driver.total_distance / 1000, 20)  # 1 point par 1000 km, max 20 points
            if driver.revenue_generated:
                score += min(driver.revenue_generated / 1000, 20)  # 1 point par 1000 unités monétaires, max 20 points
            driver.performance_score = max(min(score, 100), 0)

    @api.depends('schedule_ids')
    def _compute_schedule_count(self):
        for driver in self:
            driver.schedule_count = len(driver.schedule_ids)

    @api.constrains('license_expiry')
    def _check_license_validity(self):
        for driver in self:
            if driver.license_expiry and driver.license_expiry < fields.Date.today():
                raise UserError(_('Le permis de conduire a expiré !'))

    #################################
    # Actions
    #################################
    def action_set_available(self):
        self.ensure_one()
        self.state = 'available'

    def action_set_off_duty(self):
        self.ensure_one()
        self.state = 'off_duty'

    def action_view_schedule(self):
        self.ensure_one()
        return {
            'name': _('Work Schedule'),
            'res_model': 'fleet.driver.schedule',
            'view_mode': 'tree,form',
            'domain': [('driver_id', '=', self.id)],
            'context': {'default_driver_id': self.id},
            'type': 'ir.actions.act_window',
        }

    def action_view_performance_report(self):
        self.ensure_one()
        return {
            'name': _('Performance Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.driver.performance.report',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_driver_id': self.id,
                'default_performance_score': self.performance_score,
                'default_total_distance': self.total_distance,
                'default_fuel_efficiency': self.fuel_efficiency_rating,
                'default_accident_count': self.accident_count,
                'default_revenue': self.revenue_generated,
            }
        }

    def action_send_reminder(self):
        # Action pour envoyer un rappel concernant le renouvellement du permis ou d'autres dates importantes
        pass
