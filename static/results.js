/**
 * 
 * @author Gian-Luca Frei & Fedor Gamper
 * @date 30.05.2018
 * @project StockSearch
 * 
 * This scripts handels the HTML output of the different results.
 * the functions getDetails, getError and getTable returns a HTML string
 * whith the result of the search.ß
 * 
 */

//Injects HTML whit chart and some calculations form an given Stock
function getDetails(ssql, resultJson) {

    var shareInfos = resultJson.description.split("<br>");

    var datefrom = resultJson.data[0].date;
    var dateto = resultJson.data[resultJson.data.length - 1].date;

    var labels = resultJson.data.map( e => e.date);

    var values = resultJson.data.map( e => e.value);

    var firstEntry = resultJson.start;
    var lastEntry = resultJson.end;

    var isin = resultJson.isin;
    var datasource = resultJson.dataSource;

    var currency = resultJson.currency;

    var latestValue = values[values.length-1];
    var changeSince1 = formatNumber((latestValue-values[values.length-2])/values[values.length-2]*100);


    var minValue =Math.min.apply(null, values);
    var dateOfMin = labels[values.indexOf(minValue)];
    minValue = formatNumber(minValue);

    var maxValue = Math.max.apply(null, values);
    var dateOfMax = labels[values.indexOf(maxValue)];
    maxValue = formatNumber(maxValue);

    var change = formatNumber(latestValue - values[0]);
    var changeInPercent = formatNumber(((latestValue - values[0])/values[0]) * 100);

    var average = formatNumber(eval(values.join('+')) / values.length);

    var shareDetails = "<p> ISIN: " + isin + "</p>" +
        "<p> Datasource: " + datasource + "</p>" +
        "<p> First entry in Database: " + firstEntry + "</p>" +
        "<p> Last entry in Database: " + lastEntry + "</p>"+
        "<p> Lastest Value: "+latestValue+" " + currency+ " " +changeSince1 +"%</p>";


    var calculedDetails = "<p>The lowest value form " + datefrom + " to " + dateto + " was <strong>" + minValue + " " + currency + "</strong> on " + dateOfMin + " . </p>" +
        "<p>The highest value form " + datefrom + " to " + dateto + "  was <strong>" + maxValue + " " + currency + "</strong> on " +dateOfMax + " . </p>" +
        "<p>The change form " + datefrom + " to " + dateto + " was <strong>" + change + " " + currency + "</strong> or <strong>" + changeInPercent + "%</strong>.</p>" +
        "<p>The average value form " + datefrom + " to " + dateto + " was <strong>" + average + " " + currency + "</strong>.</p>";


    $("#results").html("<div class='d-flex' id='titleAndBack'>" +
        "<h2 class='mb-4' id='searchTitle'>" + resultJson.name + " from " + datefrom + " to " + dateto + "</h2>" +
        "<div class='ml-auto'>" +
        "<a class='nav-link' id='backButton' href='javascript:void(0)' onclick='goBack()'>" +
        "<h5 class='gray'>Back</h5>" +
        "</a></div></div>" +
        "<h6 id='description'>" + shareInfos[0] + "</h6>" +
        "<div id='details'>" +
        "<hr><div id='shareDetails'>" + shareDetails + "</div>" +
        "<hr><canvas id='myChart' width='400' height='150'></canvas>" +
        "<hr><div id='calcDetails'>" + calculedDetails + "</div>");

    //create Chart with chart.js
    $(document).ready(function () {
        var ctx = document.getElementById("myChart");
        var myChart = new Chart(ctx.getContext('2d'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'value',
                    data: values,
                    lineTension: 0.02,
                    lineThickness: 1,
                    radius: 0,
                    fill: false,
                    borderColor: "#62A910",
                    pointBackgroundColor: "#62A910"

                }]
            },
            options: {
                legend: {
                    display: false
                },
                tooltips: {
                    enabled: true
                }
            }
        });
    });


}

//Injects HTML whit the error message returned by the server
function getError(textStatus, errorThrown, error) {
    if (errorThrown === "BAD REQUEST"){
        var tmp = error.split(/(?:Expected|: Found)+/);
        var expected = tmp[1];
        var found = tmp[2];

        $("#results").html("<div class='alert alert-danger r-8 mb-4' role='alert' id='error'>" +
            "<button class='close' id='closeError' type='button' onclick='closeError()'>" +
            "<span aria-hidden='true'>&times;</span></button>" +
            "<p class='mb-2'>Error found: " + found + "</p>" +
            "<p class='mb-2'>Expected: " + expected + "</p>");
    }
    //if error isn't a false user input
    else{
        $("#results").html("<div class='alert alert-danger r-8 mb-4' role='alert' id='error'>" +
            "<button class='close' id='closeError' type='button' onclick='closeError()'>" +
            "<span aria-hidden='true'>&times;</span></button>" +
            "<p class='mb-2'>Error Status: " + textStatus + "</p>" +
            "<p class='mb-2'>Error Thrown: " + errorThrown + "</p>");
    }

}

//Injects HTML whit a Table containing the stock informations of multiple stocks
function getTable(ssql, resultJson) {


    //response has at least one entry
    if (resultJson.data.length !== 0) {
        var rows = Object.keys(resultJson.data[0]);

        var resultTable = "<thead class='background-green'><tr>";

        //fill Table with row titles
        rows.forEach(function (rowTitle) {
            resultTable += "<th>" + rowTitle.capitalize() + "</th>";
        });

        resultTable += "</tr> </thread> <tbody>";


        // Fill Rows whit details of Stocks
        resultJson.data.forEach(function (rowEntry) { //foreach entry
            resultTable += "<tr onClick='searchDetails(\"" + rowEntry["key"] + "\")'>";//link for geting details of that entry
            rows.forEach(function (rowTitle) { //for each data of the entry
                var entryData = rowEntry[rowTitle];
                if(Number(entryData) === entryData){//check if number is a number
                    entryData = formatNumber(entryData);
                }
                resultTable += "<td>" +  entryData  + "</td>";
            });
            resultTable += "</tr>";
        });
        resultTable += "</tbody>";

        $("#results").html("<div class='d-flex' id='titleAndBack'>" +
            "<h2 class='mb-4' id='searchTitle'>" + ssql + "</h2>" +
            "<div class='ml-auto'>" +
                "<div class='d-flex'>"+
                    "<a id='dlink' style='display:none;'></a>"+
                    "<a class='nav-link' id='download' href='javascript:void(0)' onclick='tableToExcel(\"resultTable\", \""+ ssql.replace(" ","_") +"\",\""+ ssql.replace(" ","_") + ".xls\")'>"+
                        "<h5 class='gray'>Export</h5>" +
                    "</a>"+
                    "<a class='nav-link' id='backButton' href='javascript:void(0)' onclick='goBack()'>" +
                        "<h5 class='gray'>Back</h5>" +
                    "</a>"+
                "</div>"+
            "</div></div>" +
            "<div class='table-responsive shadow r-8 mb-4' id='tableDiv'>" +
                "<table class='table table-striped borderless mb-1 tablesorter' id='resultTable' style='width: 100%'>" +
                 resultTable + "</table>"+
            "</div>");

        $(document).ready(function()
            {
                $("#resultTable").tablesorter();
            }
        );

    } else
        getError("no data found", "", "");
}

//Formates number n by rounding them to 2 dezimals and formats them to 2 numbers after the dot
function formatNumber(n) {//format Number
    n = Math.round(n * 100) / 100;
    if (!(n % 1 < 0.01)) {
        return n.toFixed(2);
    }
    return n;
}

//Takes the first letter of a String and puts it to uppercase
String.prototype.capitalize = function () {
    return this.charAt(0).toUpperCase() + this.slice(1);
};
