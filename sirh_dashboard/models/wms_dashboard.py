# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
import logging

log = logging.getLogger(__name__)

class FleetDashboard(models.TransientModel):
    _name = 'dashboard'
    _description = 'Fleet Dashboard'

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)
    
    # Statistiques Véhicules
    total_vehicles = fields.Integer(string='Total Vehicles')
    available_vehicles = fields.Integer(string='Available Vehicles')
    in_maintenance_vehicles = fields.Integer(string='Vehicles in Maintenance')
    reserved_vehicles = fields.Integer(string='Reserved Vehicles')
    
    # Statistiques Maintenance
    pending_maintenance = fields.Integer(string='Pending Maintenance')
    ongoing_maintenance = fields.Integer(string='Ongoing Maintenance')
    maintenance_cost_mtd = fields.Float(string='Maintenance Cost MTD')
    maintenance_cost_ytd = fields.Float(string='Maintenance Cost YTD')
    
    # Statistiques Carburant
    fuel_consumption_mtd = fields.Float(string='Fuel Consumption MTD (L)')
    fuel_cost_mtd = fields.Float(string='Fuel Cost MTD')
    avg_fuel_efficiency = fields.Float(string='Average Fuel Efficiency (L/100km)')
    total_fuel_cost_ytd = fields.Float(string='Total Fuel Cost YTD')
    
    # Statistiques Conducteurs
    total_drivers = fields.Integer(string='Total Drivers')
    available_drivers = fields.Integer(string='Available Drivers')
    on_duty_drivers = fields.Integer(string='On Duty Drivers')
    off_duty_drivers = fields.Integer(string='Off Duty Drivers')
    
    # Statistiques Réservations
    active_reservations = fields.Integer(string='Active Reservations')
    upcoming_reservations = fields.Integer(string='Upcoming Reservations')
    completed_reservations_mtd = fields.Integer(string='Completed Reservations MTD')
    reservation_revenue_mtd = fields.Float(string='Reservation Revenue MTD')
    
    # Statistiques Documents
    expiring_documents = fields.Integer(string='Expiring Documents')
    expired_documents = fields.Integer(string='Expired Documents')
    documents_expiring_soon = fields.Integer(string='Documents Expiring Soon')
    
    # Statistiques Financières
    total_revenue_mtd = fields.Float(string='Total Revenue MTD')
    total_expenses_mtd = fields.Float(string='Total Expenses MTD')
    profit_mtd = fields.Float(string='Profit MTD')
    profit_margin = fields.Float(string='Profit Margin (%)')

    @api.model
    def get_data(self):
        uid = self.env.uid
        employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', uid)], limit=1)
        log.critical('Utilisateur Connecté id : %s Name : %s', uid, employee_id.user_id.name)
        manager = "Oui" if self.env.user.has_group('crh_employe.group_hr_user_manager_1') else "Non"
        employee_id.sudo().write({'is_manager': manager})
        log.critical("Is manager : %s", employee_id.is_manager)

        isAdmin = True

        vehicle_stats = self._get_vehicle_stats()
        maintenance_stats = self._get_maintenance_stats()
        fuel_stats = self._get_fuel_stats()
        driver_stats = self._get_driver_stats()
        reservation_stats = self._get_reservation_stats()
        document_stats = self._get_document_stats()
        financial_stats = self._get_financial_stats()

        return {
            'isAdmin': isAdmin,
            'show_group_evaluation': self.env.user.has_group('sirh_evaluation.group_hr_evaluation'),
            'super_admin': self.env.user.has_group('hr.group_hr_manager'),

            # 'matricule': employee_id.matricule,
            'name': employee_id.name,
            # 'cuid': employee_id.cuid,
            # 'birthday': employee_id.birthday,
            'work_email': employee_id.work_email,
            # 'mobile_phone': employee_id.mobile_phone,
            # 'image': employee_id.image_1920,

            # 'direction': employee_id.direction_id.name,
            # 'departement': employee_id.departement_id.name,
            # 'manager': employee_id.manager_id.name,

            # 'date_start': employee_id.date_start,
            # 'poste': employee_id.poste_id.name,
            # 'type': employee_id.type_id.name,
            # 'employeur': employee_id.employeur_id.name,
            # 'type_agent': employee_id.type_agent,

            'total_vehicles': vehicle_stats['total_vehicles'],
            'available_vehicles': vehicle_stats['available_vehicles'],
            'in_maintenance_vehicles': vehicle_stats['in_maintenance_vehicles'],
            'reserved_vehicles': vehicle_stats['reserved_vehicles'],

            'pending_maintenance': maintenance_stats['pending_maintenance'],
            'ongoing_maintenance': maintenance_stats['ongoing_maintenance'],
            'maintenance_cost_mtd': maintenance_stats['maintenance_cost_mtd'],
            'maintenance_cost_ytd': maintenance_stats['maintenance_cost_ytd'],

            'fuel_consumption_mtd': fuel_stats['fuel_consumption_mtd'],
            'fuel_cost_mtd': fuel_stats['fuel_cost_mtd'],
            'avg_fuel_efficiency': fuel_stats['avg_fuel_efficiency'],
            'total_fuel_cost_ytd': fuel_stats['total_fuel_cost_ytd'],

            'total_drivers': driver_stats['total_drivers'],
            'available_drivers': driver_stats['available_drivers'],
            'on_duty_drivers': driver_stats['on_duty_drivers'],
            'off_duty_drivers': driver_stats['off_duty_drivers'],

            'active_reservations': reservation_stats['active_reservations'],
            'upcoming_reservations': reservation_stats['upcoming_reservations'],
            'completed_reservations_mtd': reservation_stats['completed_reservations_mtd'],
            'reservation_revenue_mtd': reservation_stats['reservation_revenue_mtd'],

            'expiring_documents': document_stats['expiring_documents'],
            'expired_documents': document_stats['expired_documents'],
            'documents_expiring_soon': document_stats['documents_expiring_soon'],

            'total_revenue_mtd': financial_stats['total_revenue_mtd'],
            'total_expenses_mtd': financial_stats['total_expenses_mtd'],
            'profit_mtd': financial_stats['profit_mtd'],
            'profit_margin': financial_stats['profit_margin'],
        }

    def _get_vehicle_stats(self):
        vehicles = self.env['fleet.vehicle'].search([])
        total_vehicles = len(vehicles)
        available_vehicles = len(vehicles.filtered(lambda v: v.is_available))
        in_maintenance_vehicles = len(vehicles.filtered(lambda v: not v.is_available and v.maintenance_log_ids.filtered(lambda m: m.state == 'in_progress')))
        reserved_vehicles = len(vehicles.filtered(lambda v: not v.is_available and v.reservation_ids.filtered(lambda r: r.state in ['confirmed', 'ongoing'])))
        return {
            'total_vehicles': total_vehicles,
            'available_vehicles': available_vehicles,
            'in_maintenance_vehicles': in_maintenance_vehicles,
            'reserved_vehicles': reserved_vehicles,
        }

    def _get_maintenance_stats(self):
        today = self.date or fields.Date.context_today(self)
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)
        maintenances = self.env['fleet.vehicle.maintenance'].search([])
        pending_maintenance = len(maintenances.filtered(lambda m: m.state == 'draft'))
        ongoing_maintenance = len(maintenances.filtered(lambda m: m.state == 'in_progress'))
        mtd_maintenances = maintenances.filtered(lambda m: m.date >= start_of_month and m.state == 'done')
        ytd_maintenances = maintenances.filtered(lambda m: m.date >= start_of_year and m.state == 'done')
        maintenance_cost_mtd = sum(mtd_maintenances.mapped('total_cost'))
        maintenance_cost_ytd = sum(ytd_maintenances.mapped('total_cost'))
        return {
            'pending_maintenance': pending_maintenance,
            'ongoing_maintenance': ongoing_maintenance,
            'maintenance_cost_mtd': maintenance_cost_mtd,
            'maintenance_cost_ytd': maintenance_cost_ytd,
        }

    def _get_fuel_stats(self):
        today = self.date or fields.Date.context_today(self)
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)
        fuel_logs = self.env['fleet.expense'].search([
            ('expense_type', '=', 'fuel'),
            ('date', '>=', start_of_month)
        ])
        fuel_consumption_mtd = sum(fuel_logs.mapped('liters'))
        fuel_cost_mtd = sum(fuel_logs.mapped('amount'))
        if fuel_consumption_mtd > 0:
            total_distance = sum(fuel_logs.mapped('vehicle_id.odometer_log_ids').filtered(lambda o: o.date >= start_of_month).mapped('distance'))
            avg_fuel_efficiency = (fuel_consumption_mtd / total_distance * 100) if total_distance else 0
        else:
            avg_fuel_efficiency = 0
        ytd_fuel_logs = self.env['fleet.expense'].search([
            ('expense_type', '=', 'fuel'),
            ('date', '>=', start_of_year)
        ])
        total_fuel_cost_ytd = sum(ytd_fuel_logs.mapped('amount'))
        return {
            'fuel_consumption_mtd': fuel_consumption_mtd,
            'fuel_cost_mtd': fuel_cost_mtd,
            'avg_fuel_efficiency': avg_fuel_efficiency,
            'total_fuel_cost_ytd': total_fuel_cost_ytd,
        }

    def _get_driver_stats(self):
        drivers = self.env['fleet.driver'].search([])
        total_drivers = len(drivers)
        available_drivers = len(drivers.filtered(lambda d: d.state == 'available'))
        on_duty_drivers = len(drivers.filtered(lambda d: d.state == 'driving'))
        off_duty_drivers = len(drivers.filtered(lambda d: d.state in ['off_duty', 'leave']))
        return {
            'total_drivers': total_drivers,
            'available_drivers': available_drivers,
            'on_duty_drivers': on_duty_drivers,
            'off_duty_drivers': off_duty_drivers,
        }

    def _get_reservation_stats(self):
        today = self.date or fields.Date.context_today(self)
        start_of_month = today.replace(day=1)
        reservations = self.env['fleet.vehicle.reservation'].search([])
        active_reservations = len(reservations.filtered(lambda r: r.state == 'ongoing'))
        upcoming_reservations = len(reservations.filtered(lambda r: r.state == 'confirmed' and r.start_date > fields.Datetime.now()))
        completed_reservations = reservations.filtered(lambda r: r.state == 'completed' and r.end_date >= start_of_month)
        completed_reservations_mtd = len(completed_reservations)
        reservation_revenue_mtd = sum(completed_reservations.mapped('revenue'))
        return {
            'active_reservations': active_reservations,
            'upcoming_reservations': upcoming_reservations,
            'completed_reservations_mtd': completed_reservations_mtd,
            'reservation_revenue_mtd': reservation_revenue_mtd,
        }

    def _get_document_stats(self):
        today = fields.Date.today()
        next_month = today + timedelta(days=30)
        documents = self.env['fleet.vehicle.document'].search([])
        expired_documents = len(documents.filtered(lambda d: d.state == 'expired'))
        documents_expiring_soon = len(documents.filtered(lambda d: d.state == 'valid' and d.expiry_date and d.expiry_date <= next_month))
        expiring_documents = expired_documents + documents_expiring_soon
        return {
            'expiring_documents': expiring_documents,
            'expired_documents': expired_documents,
            'documents_expiring_soon': documents_expiring_soon,
        }

    def _get_financial_stats(self):
        today = self.date or fields.Date.context_today(self)
        start_of_month = today.replace(day=1)
        expenses = self.env['fleet.expense'].search([('date', '>=', start_of_month)])
        reservations = self.env['fleet.vehicle.reservation'].search([
            ('state', '=', 'completed'),
            ('end_date', '>=', start_of_month)
        ])
        total_expenses_mtd = sum(expenses.mapped('amount'))
        total_revenue_mtd = sum(reservations.mapped('revenue'))
        profit_mtd = total_revenue_mtd - total_expenses_mtd
        profit_margin = (profit_mtd / total_revenue_mtd * 100) if total_revenue_mtd else 0
        return {
            'total_expenses_mtd': total_expenses_mtd,
            'total_revenue_mtd': total_revenue_mtd,
            'profit_mtd': profit_mtd,
            'profit_margin': profit_margin,
        }

    @api.model
    def get_custom_dashboard_data(self):
        # Graphique 1 : Maintenance Cost par Véhicule (MTD)
        var_vehicles = self.env['fleet.vehicle'].search([])
        graph1_labels = []
        graph1_values = []
        for veh in var_vehicles:
            graph1_labels.append(veh.name or "N/A")
            graph1_values.append(veh.maintenance_cost_total or 0.0)
        
        # Graphique 2 : Fuel Cost MTD par Conducteur
        var_drivers = self.env['fleet.driver'].search([])
        graph2_labels = []
        graph2_values = []
        for drv in var_drivers:
            graph2_labels.append(drv.name or "N/A")
            fuel_expenses = self.env['fleet.expense'].search([
                ('expense_type', '=', 'fuel'),
                ('driver_id', '=', drv.id),
                ('date', '>=', fields.Date.today().replace(day=1))
            ])
            graph2_values.append(sum(fuel_expenses.mapped('amount')))
        
        # Tableau de détails : Top 5 véhicules par coût de maintenance
        details = []
        sorted_vehicles = var_vehicles.sorted(lambda v: v.maintenance_cost_total, reverse=True)[:5]
        for veh in sorted_vehicles:
            details.append({
                'vehicle': veh.name,
                'driver': veh.current_driver_id.name if veh.current_driver_id else "",
                'maintenance_cost': veh.maintenance_cost_total or 0.0,
                'fuel_cost_mtd': 0.0,  # À ajuster si besoin
            })

        return {
            'graph1_labels': graph1_labels,
            'graph1_values': graph1_values,
            'graph2_labels': graph2_labels,
            'graph2_values': graph2_values,
            'details': details,
        }

class SirhEmployee(models.Model):
    _name = "hr.employee"
    _inherit = ["hr.employee"]

    is_manager = fields.Char("Is Manager")
