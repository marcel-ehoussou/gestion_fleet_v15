odoo.define("wms.WmsDashboard", function (require) {
    "use strict";

    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;
    var _t = core._t;

    var DashboardView = AbstractAction.extend({
        events: _.extend({}, Widget.prototype.events, {}),
        init: function (parent, context) {
            this._super.apply(this, arguments);
            this.wms_data = {};
        },
        start: function () {
            var self = this;
            return this._rpc({
                model: 'dashboard',
                method: 'get_data',
                args: [],
            }).then(function (result) {
                self.wms_data = result;
                console.log('---- wms_data ----', self.wms_data);
            }).then(function () {
                var content = QWeb.render('WmsDashboardTemplate', {widget: self});
                self.$el.html(content);
            }).then(function () {
                // Attendre que le DOM soit complètement chargé
                setTimeout(function () {
                    self.drawVehicleStatusChart();
                }, 500);
            });
        },
        do_show: function () {
            var show = this._super.apply(this, arguments);
            $(".o_control_panel").addClass("o_hidden");
            return show;
        },
        destroy: function () {
            $(".o_control_panel").removeClass("o_hidden");
            return this._super.apply(this, arguments);
        },
        drawVehicleStatusChart: function() {
            var self = this;
            var container = self.$el.find('#vehicleStatusChart');
            if (container.length === 0) {
                console.error("Le conteneur 'vehicleStatusChart' est introuvable !");
                return;
            }
            
            // S'assurer que le conteneur a une hauteur définie
            container.css('height', '300px');
            
            try {
                Highcharts.chart('vehicleStatusChart', {
                    chart: {
                        type: 'pie',
                        height: 300
                    },
                    title: {
                        text: 'Statistiques Véhicules'
                    },
                    plotOptions: {
                        pie: {
                            innerSize: '50%',  // Doughnut chart
                            dataLabels: {
                                enabled: false
                            }
                        }
                    },
                    series: [{
                        name: 'Véhicules',
                        data: [
                            { name: 'Disponible', y: self.wms_data.available_vehicles || 0, color: '#28a745' },
                            { name: 'Maintenance', y: self.wms_data.in_maintenance_vehicles || 0, color: '#ffc107' },
                            { name: 'Réservé', y: self.wms_data.reserved_vehicles || 0, color: '#17a2b8' }
                        ]
                    }],
                    legend: {
                        align: 'center',
                        verticalAlign: 'bottom',
                        layout: 'horizontal'
                    }
                });
            } catch (error) {
                console.error("Erreur lors de l'initialisation du graphique:", error);
            }
        }
    });

    core.action_registry.add('wms_dashboard_view', DashboardView);
    return DashboardView;
});
