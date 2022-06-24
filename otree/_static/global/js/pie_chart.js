console.log("pie chart ready!")


// vars from oTree
let dictators = js_vars.dictators;
let role = js_vars.role;

// initiate variables
var green;
var red;
var primary = "#0275d8";
var pie;

// set values

if(role=="Recipient"){
    red = dictators;
    green = 100 -  red;
}else{
    green = dictators;
    red = 100 - green;
}

// set colors
const pattern = "M 0 0 L 10 10 M 9 -1 L 11 1 M -1 9 L 1 11"; //"M 3 0 L 3 10 M 8 0 L 8 10"; // more patterns here: https://www.highcharts.com/docs/chart-design-and-style/pattern-fills
const yourColor = "#36D6B0";
const yourLabel = {
    backgroundColor: "rgba(255, 255, 255, 0.33)",
    style: {
        fontWeight: "normal",
        textOutline: 0,
    },
};

const othersColor = {
    pattern: {
        path: pattern,
        color: "#FF0B5F",
        width: 10,
        height: 10,
        patternTransform: "scale(2)"
    }
};
const othersLabel = {
    style: {
        color: "#000000"
    }
}


// viz
Highcharts.chart('container', {
    chart: {
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        type: 'pie',
        exporting: {
                enabled: false
              },
    },

    title: {
                text: ""
              },

    tooltip: {
        formatter: function() {
                  if (this.point.color == yourColor) {
                    return "Your share";
                  } else {
                    return "The other participant's share"
                  }
                }
    },
    accessibility: {
        point: {
            valueSuffix: 'points'
        }
    },
    plotOptions: {
        pie: {
            allowPointSelect: true,
            cursor: 'pointer',
            dataLabels: {
                enabled: true,
                format: '<b>{point.name}</b>: {point.percentage} %',
                distance: 15,
                style: {
                      fontWeight: "normal"
                    }
            }
        }
    },
    series: [{
        name: 'Allocation',
        colorByPoint: true,
        data: [{
            name: "The Other's Share",
            y: red,
            sliced: true,
            selected: true,
            color: othersColor
        }, {
            name: 'Your Share',
            y: green,
            color: yourColor
        }]
    }]
});

/*

// define pie chart
$(function () {
	$(document).ready(function(){

		$('.pieChart').each(function(){

            pie = new Highcharts.chart({
              exporting: {
                enabled: false
              },
              chart: {
                renderTo: this,
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: "pie",
                backgroundColor: "transparent"
              },
              title: {
                text: ""
              },
              tooltip: {
                formatter: function() {
                  if (this.point.color == successColor) {
                    return "You win 10 euros.";
                  } else {
                    return "You win nothing."
                  }
                }
              },
              accessibility: {
                point: {
                  valueSuffix: "%"
                }
              },
              plotOptions: {
                pie: {
                  allowPointSelect: true,
                  cursor: "pointer",
                  dataLabels: {
                    distance: 15,
                    enabled: true,
                    format: "{point.percentage:.0f} %", //"<b>{point.name}</b>: {point.percentage:.0f} %"
                    style: {
                      fontWeight: "normal"
                    }
                  },
                }
              },
              series: [{
                name: "balls",
                colorByPoint: true,
                data: [{
                    name: "red",
                    y: red,
                    sliced: true,
                    selected: true,
                    color: lossColor
                  },
                  {
                    name: "green",
                    y: green,
                    sliced: true,
                    selected: true,
                    color: successColor
                  }
                ]
              }]
            });
         });
	});
});*/
