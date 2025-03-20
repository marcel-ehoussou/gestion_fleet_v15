from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    # Gestion du carburant
    fuel_log_ids = fields.One2many('fleet.vehicle.fuel.log', 'vehicle_id', string='Journaux de carburant')
    fuel_efficiency = fields.Float(string='Efficacité énergétique (L/100km)', compute='_compute_fuel_efficiency')
    last_fuel_cost = fields.Float(string='Dernier coût de carburant', compute='_compute_last_fuel_cost')
    
    # Maintenance et réparations
    maintenance_log_ids = fields.One2many('fleet.vehicle.maintenance', 'vehicle_id', string='Journaux de maintenance')
    next_maintenance_date = fields.Date(string='Date de la prochaine maintenance', compute='_compute_next_maintenance', store=True)
    maintenance_cost_total = fields.Float(string='Coût total de maintenance', compute='_compute_maintenance_cost')
    service_count = fields.Integer(string='Nombre de services', compute='_compute_service_count')
    service_activity = fields.Selection([
        ('overdue', 'En retard'),
        ('today', 'Aujourd\'hui'),
        ('planned', 'Planifié'),
        ('none', 'Aucun'),
    ], string='Activité de service', compute='_compute_service_activity')
    
    # Autres dépenses
    insurance_ids = fields.One2many('fleet.vehicle.insurance', 'vehicle_id', string='Enregistrements d\'assurance')
    technical_inspection_ids = fields.One2many('fleet.vehicle.inspection', 'vehicle_id', string='Inspections techniques')
    current_insurance_id = fields.Many2one('fleet.vehicle.insurance', string='Assurance actuelle', compute='_compute_current_insurance')
    
    # Suivi du kilométrage
    odometer_log_ids = fields.One2many('fleet.vehicle.odometer.log', 'vehicle_id', string='Journaux du compteur kilométrique')
    last_odometer = fields.Float(string='Dernière lecture du compteur kilométrique', compute='_compute_last_odometer')
    daily_usage = fields.Float(string='Utilisation quotidienne moyenne (km)', compute='_compute_daily_usage')
    
    # Documents
    document_ids = fields.One2many('fleet.vehicle.document', 'vehicle_id', string='Documents')
    document_count = fields.Integer(string='Nombre de documents', compute='_compute_document_count')
    
    # Réservations
    reservation_ids = fields.One2many('fleet.vehicle.reservation', 'vehicle_id', string='Réservations')
    is_available = fields.Boolean(string='Disponible', compute='_compute_availability', store=True)
    current_driver_id = fields.Many2one('fleet.driver', string='Conducteur actuel', compute='_compute_availability')
    
    maintenance_due = fields.Boolean(string="Maintenance due", compute="_compute_maintenance_due", store=True)
    # Nouveau champ bill_count (par exemple, le nombre de factures liées)
    bill_count = fields.Integer(
        string="Bill Count",
        compute="_compute_bill_count",
        store=True
    )
    
    @api.depends('revenue_ids')  # ou tout autre champ pertinent
    def _compute_bill_count(self):
        for vehicle in self:
            # Exemple simple : on suppose qu'il n'y a pas de factures, ou à adapter
            vehicle.bill_count = 0

    @api.depends("next_maintenance_date")
    def _compute_maintenance_due(self):
        today = fields.Date.today()
        for vehicle in self:
            vehicle.maintenance_due = vehicle.next_maintenance_date and vehicle.next_maintenance_date <= today

    # Suivi des revenus
    revenue_ids = fields.One2many('fleet.vehicle.revenue', 'vehicle_id', string='Enregistrements de revenus')
    total_revenue = fields.Float(string='Revenu total', compute='_compute_total_revenue')
    profitability = fields.Float(string='Rentabilité (%)', compute='_compute_profitability', store=True)
    
    @api.depends('fuel_log_ids', 'odometer_log_ids')
    def _compute_fuel_efficiency(self):
        for vehicle in self:
            if len(vehicle.odometer_log_ids) >= 2:
                sorted_logs = vehicle.odometer_log_ids.sorted('date')
                distance = sorted_logs[-1].value - sorted_logs[0].value
                total_fuel = sum(vehicle.fuel_log_ids.mapped('liters'))
                if distance > 0 and total_fuel > 0:
                    vehicle.fuel_efficiency = (total_fuel * 100) / distance
                else:
                    vehicle.fuel_efficiency = 0
            else:
                vehicle.fuel_efficiency = 0
            
    @api.depends('maintenance_log_ids', 'maintenance_log_ids.state', 'maintenance_log_ids.date')
    def _compute_next_maintenance(self):
        for vehicle in self:
            upcoming_maintenances = vehicle.maintenance_log_ids.filtered(
                lambda m: m.state == 'scheduled' and m.date > fields.Date.today()
            ).sorted('date')
            vehicle.next_maintenance_date = upcoming_maintenances[0].date if upcoming_maintenances else False

    @api.depends('odometer_log_ids', 'odometer_log_ids.date', 'odometer_log_ids.value')
    def _compute_daily_usage(self):
        for vehicle in self:
            logs = vehicle.odometer_log_ids.sorted('date')
            if len(logs) >= 2:
                # On convertit la date en objet date (si ce n'est pas déjà le cas)
                first_date = fields.Date.from_string(logs[0].date)
                last_date = fields.Date.from_string(logs[-1].date)
                days = (last_date - first_date).days
                if days > 0:
                    vehicle.daily_usage = (logs[-1].value - logs[0].value) / days
                else:
                    vehicle.daily_usage = 0.0
            else:
                vehicle.daily_usage = 0.0

    @api.depends('document_ids')
    def _compute_document_count(self):
        for vehicle in self:
            vehicle.document_count = len(vehicle.document_ids)

    @api.depends('fuel_log_ids')
    def _compute_last_fuel_cost(self):
        for vehicle in self:
            # Si des logs de carburant existent, on prend le dernier log basé sur la date
            if vehicle.fuel_log_ids:
                sorted_logs = vehicle.fuel_log_ids.sorted(key=lambda l: l.date, reverse=True)
                last_log = sorted_logs[0]
                vehicle.last_fuel_cost = last_log.total_amount or 0.0
            else:
                vehicle.last_fuel_cost = 0.0


    @api.depends('odometer_log_ids', 'odometer_log_ids.value')
    def _compute_last_odometer(self):
        for vehicle in self:
            if vehicle.odometer_log_ids:
                # Trier les logs par date décroissante pour récupérer le dernier
                sorted_logs = vehicle.odometer_log_ids.sorted(key=lambda l: l.date, reverse=True)
                vehicle.last_odometer = sorted_logs[0].value or 0.0
            else:
                vehicle.last_odometer = 0.0


    @api.depends('maintenance_log_ids.total_cost')
    def _compute_maintenance_cost(self):
        for vehicle in self:
            vehicle.maintenance_cost_total = sum(vehicle.maintenance_log_ids.mapped('total_cost'))
            
    @api.depends('insurance_ids')
    def _compute_current_insurance(self):
        today = fields.Date.today()
        for vehicle in self:
            current_insurance = vehicle.insurance_ids.filtered(
                lambda i: i.state == 'valid' and 
                          i.start_date <= today and 
                          (not i.end_date or i.end_date >= today)
            )
            vehicle.current_insurance_id = current_insurance[0] if current_insurance else False
            
    @api.depends('reservation_ids', 'reservation_ids.state', 'reservation_ids.start_date', 'reservation_ids.end_date')
    def _compute_availability(self):
        now = fields.Datetime.now()
        for vehicle in self:
            current_reservation = vehicle.reservation_ids.filtered(
                lambda r: r.state == 'confirmed' and 
                          r.start_date <= now and 
                          r.end_date >= now
            )
            vehicle.is_available = not bool(current_reservation)
            if current_reservation:
                vehicle.current_driver_id = current_reservation[0].driver_id
            else:
                vehicle.current_driver_id = False


    @api.depends('revenue_ids', 'revenue_ids.amount')
    def _compute_total_revenue(self):
        for vehicle in self:
            vehicle.total_revenue = sum(vehicle.revenue_ids.mapped('amount'))
            
    @api.depends('revenue_ids', 'revenue_ids.amount', 'maintenance_cost_total', 'fuel_log_ids', 'fuel_log_ids.total_amount')
    def _compute_profitability(self):
        for vehicle in self:
            total_revenue = sum(vehicle.revenue_ids.mapped('amount'))
            total_cost = vehicle.maintenance_cost_total + \
                        sum(vehicle.fuel_log_ids.mapped('total_amount'))
            if total_cost > 0:
                vehicle.profitability = (total_revenue - total_cost) / total_cost * 100
            else:
                vehicle.profitability = 0
            
    def action_schedule_maintenance(self):
        # Action pour planifier la maintenance
        pass
        
    def action_create_reservation(self):
        # Action pour créer une nouvelle réservation
        pass
        
    def action_view_documents(self):
        # Action pour voir les documents associés
        pass
        
    def action_report_analytics(self):
        # Action pour générer un rapport analytique
        pass

    @api.depends('maintenance_log_ids')
    def _compute_service_count(self):
        for vehicle in self:
            vehicle.service_count = len(vehicle.maintenance_log_ids)

    @api.depends('maintenance_log_ids', 'next_maintenance_date')
    def _compute_service_activity(self):
        today = fields.Date.today()
        for vehicle in self:
            if not vehicle.next_maintenance_date:
                vehicle.service_activity = 'none'
                continue

            if vehicle.next_maintenance_date < today:
                vehicle.service_activity = 'overdue'
            elif vehicle.next_maintenance_date == today:
                vehicle.service_activity = 'today'
            else:
                vehicle.service_activity = 'planned'

    def return_action_to_open(self):
        """ Ouvre la vue xml spécifiée dans xml_id pour le véhicule actuel """
        self.ensure_one()
        xml_id = self._context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window']._for_xml_id('fleet_advanced_management.' + xml_id)
            res.update(context=dict(self.env.context, default_vehicle_id=self.id, group_by=False))
            return res
        return False
