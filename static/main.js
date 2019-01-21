/**
* @author Gian-Luca Frei & Fedor Gamper
* @date 30.05.2018
* @project StockSearch
*
*
*
* This Scripts handels the advanced mode and the connection to the api.
*
* It also contains a function to export the result table, a function 
* that goes back to previeous searches and the logic to swich from 
* advanced mode to the easy modeß
* 
*/

//Method called by change Mode
function changeMode() {
    if ($("#mode").html() === "EASY MODE") {
        $("#mode").html("ADVANCED MODE"); //Change title of menu link
        $("#advancedMode").css("display", "none"); // hide Advance Mode elements
        $("#easyMode").css("display", "block"); // unhide Easy Mode elements
    } else {
        $("#mode").html("EASY MODE"); //Change title of menu link
        $("#easyMode").css("display", "none"); // hide Easy Mode elements
        $("#advancedMode").css("display", "flex"); // unhide Advance Mode elements

    }
}

//function called by press on Advanced Search button
function getAdvancedResults() {
    var ssql = $("#query").val();
    getResults(ssql)
}

//Method called by search button
function getResults(ssql) {
    $(document).ready(function () {

        if (ssql !== "" && ssql !== undefined) {


            var url = "/?q=" + encodeURIComponent(ssql.trim());
            console.log("GET: " + url);
            var myJson;

            $.ajax({
                type: 'GET',
                dataType: 'json',
                localCache: true,
                cacheTTL: 1, //chache deleted after one hour
                url: url,
                timeout: 50000,
                success: function (response, textStatus) {
                    saveSearch(ssql);
                    switch (response.type) {
                        case "table":
                            getTable(ssql, response);
                            break;
                        case "detail":
                            getDetails(ssql, response);
                            break;
                        default:
                            getError({"errorType": "False Respond type"});
                            break;
                    }
                    $("#results").css("display","block");

                },
                error: function (xhr, textStatus, errorThrown) {
                    saveSearch("error");
                    $("#results").css("display","block");
                    if(typeof xhr.responseText != "undefined") {
                        getError(textStatus, errorThrown, JSON.parse(xhr.responseText)["error"]);
                    }
                    else {
                        getError((textStatus, errorThrown, "server not responding"));
                    }
                }
            });
        }
    })
}


//Method called by click on Table
function searchDetails(Company) {

    var ssql = "GET \'" + Company + "\'";
    $("#query").val(ssql);

    getResults(ssql);

}


//Closes warning and error blocks and resets them to the default value
function closeError() {
    document.getElementById('results').removeChild(document.getElementById('error'));
    $('#results').css("display" , "none");
}


//bind Enter Key to input field
$(document).ready(function () {
    var input = document.getElementById("query");
    input.addEventListener("keyup", function (event) {
        event.preventDefault();
        if (event.keyCode === 13) {
            document.getElementById("AdvancedSearchButton").click();
        }
    });
});


//instanciate and/or updates sessionStorage for back button
function saveSearch(ssql) {
    var queries = JSON.parse(sessionStorage.getItem("queries"));
    if (queries === null) {
        queries = []; // create new list
    }
    queries.push(ssql);
    sessionStorage.queries = JSON.stringify(queries);
}

//function called by click on back button/link
function goBack() {

    var queries = JSON.parse(sessionStorage.getItem("queries")); //load previous queries out of sessionStorage

    if (queries.length >= 2) {
        queries.pop();//the Query shown now. first query stays in the list
    }
    var lastquery = queries.pop();//get the last search query

    while (lastquery === "error") { //errors are skipped and not shown again
        lastquery = queries.pop();
    }

    sessionStorage.queries = JSON.stringify(queries); //save previous queries out of sessionStorage

    if (lastquery !== undefined) {
        getResults(lastquery);
    }
}

//show loading gif
$(document).ready(function () {
    $(document).ajaxStart(function () {
    $(".search").each(function () {
        $(this).html($(this).html().replace("Search",""));
    });
    $(".loadingAnimation").each(function () {
            $(this).css("display", "block");
        });
        document .getElementById("results").style.display = "none";

    }).ajaxStop(function () {
        $(".search").each(function () {
            $(this).html($(this).html() + "Search");
        });
        $(".loadingAnimation").each(function () {
            $(this).css("display", "None");
        });
    });
});

//source: https://stackoverflow.com/questions/17126453/html-table-to-excel-javascript
    var tableToExcel = (function () {
        var uri = 'data:application/vnd.ms-excel;base64,'
            , template = '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40"><head><!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets><x:ExcelWorksheet><x:Name>{worksheet}</x:Name><x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions></x:ExcelWorksheet></x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]--></head><body><table>{table}</table></body></html>'
            , base64 = function (s) { return window.btoa(unescape(encodeURIComponent(s))) }
            , format = function (s, c) { return s.replace(/{(\w+)}/g, function (m, p) { return c[p]; }) };
        return function (table, name, filename) {
            if (!table.nodeType) table = document.getElementById(table);
            var ctx = { worksheet: name || 'Worksheet', table: table.innerHTML };

            document.getElementById("dlink").href = uri + base64(format(template, ctx));
            document.getElementById("dlink").download = filename;
            document.getElementById("dlink").click();

        }
    })();