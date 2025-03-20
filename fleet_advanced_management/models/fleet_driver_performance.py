from odoo import models, fields, api, _

class FleetDriverPerformanceReport(models.TransientModel):
    _name = 'fleet.driver.performance.report'
    _description = 'Rapport de Performance du Conducteur'

    driver_id = fields.Many2one('fleet.driver', string='Conducteur', required=True)
    date = fields.Date(string='Date du Rapport', default=fields.Date.today)
    
    # Indicateurs de Performance
    performance_score = fields.Float(string='Score de Performance Global')
    total_distance = fields.Float(string='Distance Totale Parcourue (km)')
    fuel_efficiency = fields.Float(string='Efficacité du Carburant')
    accident_count = fields.Integer(string='Nombre d\'Accidents')
    revenue = fields.Float(string='Revenu Généré')
    
    # Analyse Détaillée
    strengths = fields.Text(string='Forces', compute='_compute_analysis')
    areas_for_improvement = fields.Text(string='Axes d\'Amélioration', compute='_compute_analysis')
    recommendations = fields.Text(string='Recommandations', compute='_compute_analysis')
    
    @api.depends('performance_score', 'total_distance', 'fuel_efficiency', 'accident_count', 'revenue')
    def _compute_analysis(self):
        for report in self:
            # Initialiser les listes pour l'analyse
            strengths = []
            improvements = []
            recommendations = []
            
            # Analyser le score de performance
            if report.performance_score >= 90:
                strengths.append(_('Performance globale exceptionnelle'))
            elif report.performance_score >= 80:
                strengths.append(_('Très bonne performance globale'))
            elif report.performance_score < 60:
                improvements.append(_('La performance globale nécessite une amélioration'))
                recommendations.append(_('Planifier une réunion d\'évaluation de performance'))
            
            # Analyser l'efficacité du carburant
            if report.fuel_efficiency >= 8:
                strengths.append(_('Excellente efficacité du carburant'))
            elif report.fuel_efficiency < 5:
                improvements.append(_('L\'efficacité du carburant pourrait être améliorée'))
                recommendations.append(_('Fournir une formation à l\'éco-conduite'))
            
            # Analyser les accidents
            if report.accident_count == 0:
                strengths.append(_('Dossier de sécurité parfait'))
            elif report.accident_count > 2:
                improvements.append(_('Le dossier de sécurité nécessite une attention particulière'))
                recommendations.append(_('Formation obligatoire à la sécurité requise'))
            
            # Analyser le revenu
            if report.revenue > 10000:
                strengths.append(_('Forte génération de revenus'))
            elif report.revenue < 5000:
                improvements.append(_('Génération de revenus en dessous de l\'objectif'))
                recommendations.append(_('Revoir l\'optimisation des itinéraires'))
            
            # Formater les textes d'analyse
            report.strengths = '\n'.join(['• ' + s for s in strengths]) if strengths else _('Aucune force notable identifiée')
            report.areas_for_improvement = '\n'.join(['• ' + i for i in improvements]) if improvements else _('Aucun axe majeur nécessitant une amélioration')
            report.recommendations = '\n'.join(['• ' + r for r in recommendations]) if recommendations else _('Aucune recommandation spécifique pour le moment')
    
    def action_print_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_name': 'fleet_advanced_management.driver_performance_report',
            'report_type': 'qweb-pdf',
            'data': {
                'doc_ids': self.ids,
                'doc_model': 'fleet.driver.performance.report',
            }
        }