function show_succes(message, title) {
  toastr.options.closeButton = true;
  toastr.options.progressBar = true;
  toastr.success(message, title);
}
function show_warning(message, title) {
  toastr.options.closeButton = true;
  toastr.options.progressBar = true;
  toastr.warning(message, title);
}
function show_error(message, title) {
  toastr.options.closeButton = true;
  toastr.options.progressBar = true;
  toastr.error(message, title);
}

function generate_highcharts_pie_chart_lite(div_id, type, title, series) {
  Highcharts.chart('div_id', {
        chart: {
            type: type
        },
        title: {
            text: '',
            align: 'left'
        },
        tooltip: {
            headerFormat: '',
            pointFormat: '<span style="color:{point.color}">\u25CF</span> <b> {point.name}</b><br/>' +
                'Area (square km): <b>{point.y}</b><br/>' +
                'Population density (people per square km): <b>{point.z}</b><br/>'
        },
        series: [{
            minPointSize: 10,
            innerSize: '20%',
            zMin: 0,
            name: 'countries',
            data: series
        }]
    });
}

function generate_highcharts_pie_chart(div_id, type, title, series, title2) {
  Highcharts.chart(div_id, {
      chart: {
          plotBackgroundColor: null,
          plotBorderWidth: null,
          plotShadow: false,
          type: type
      },
      title: {
          text: title
      },
      tooltip: {
          pointFormat: '{series.name}: <b>{point.y:.0f}</b>'
      },
      plotOptions: {
          pie: {
              allowPointSelect: true,
              cursor: 'pointer',
              dataLabels: {
                  enabled: true,
                  format: '<b>{point.name}</b>',
                  style: {
                      color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                  }
              }
          }
      },
      series: [{
          name: title2,
          colorByPoint: true,
          data: series
      }],
      credits: {
          enabled: false
      },
  });
}

function generate_highcharts_negative_columns(div_id, type, title, categories , series) {
  return Highcharts.chart(div_id, {
      chart: {
          type: type
      },
      title: {
          text: title
      },
      xAxis: {
          categories: categories
      },
      yAxis: {
          title: {
              text: 'Nombre de fiche'
          }
      },
      credits: {
          enabled: false
      },
      series: series
  });
}

function generate_highcharts_negative_columns_lite(div_id, type, title, categories , series) {
  return Highcharts.chart(div_id, {
      chart: {
          type: type
      },
      title: {
          text: title
      },
      xAxis: {
          categories: categories
      },
      yAxis: {
          title: {
              text: 'Montants'
          }
      },
      credits: {
          enabled: false
      },
      series: series
  });
}
