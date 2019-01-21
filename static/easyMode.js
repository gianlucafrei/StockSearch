/**
 * @author Gian-Luca Frei & Fedor Gamper
 * @date 30.05.2018
 * @project StockSearch
 * 
 * This Script handels the generation of the search query in the Easy Mode.
 * It defines the apperence of the filters, the imputs for the filters, 
 * the additon of a filter to the search query and the remuval of a filter out 
 * of the search query.
 * 
 * 
 * A Filter looks like this:
 * <div class="filter">
 *         FilterString]
 *            <button class"close>...</button>
 *       </div>
 *
 */

/**
 * Deletes a filter out of the HTML-DOM when pushed on the x button of the filter.
 * @param filter = div object of filter containing of the button and the filter string
 */
function deleteFilter(filter) {
   var ssql = document.getElementById("ssql");
   if(filter.innerText.indexOf("WHERE")!== -1){
       ssql.innerHTML = ssql.innerHTML.replace(filter.outerHTML, "");
       if(ssql.children.length !== 2){
           ssql.children.item(1).firstChild.outerHTML = "<p class='m-0 pt-2 pr-2'>WHERE</p>";
       }
   }else{

       ssql.innerHTML = ssql.innerHTML.replace(filter.outerHTML, "");
   }
}

/**
 * Injects the Filter div on the right place in the such object
 * @param filterHTML = the filter div that has to be added in the HTML-Dom
 */
function renderFilter(filterHTML) {
    var ssql = document.getElementById("ssql");
    var button = ssql.children.item(ssql.children.length-1);

    var concatunate ="<div id='concat'><select class='form-control form-control-sm' id='concatunate'onchange='switchConcatState(this.parentElement.parentElement)'>" +
        "<option>OR</option>" +
        "<option>AND</option>" +
        "</select></div>";

    var wrapper = document.createElement("div");
    wrapper.setAttribute("class", "row m-0");

    if (ssql.children.length === 2) {

        wrapper.innerHTML = "<p class='m-0 pt-2 pr-2'>WHERE</p>" + filterHTML;
        ssql.insertBefore(wrapper, button);
    }else{
        wrapper.innerHTML = concatunate + filterHTML;
        ssql.insertBefore(wrapper, button);
        }

    }

/**
 * Methode called when pushed on Search in easy mode
 * Generates the ssql statement
 */
function getEasyResults() {

    var filters = document.getElementById("ssql").children;
    var ssql = "";

    if (filters.length > 2) {
        /*Add "ALL Shares Where" and the first filter to the list.
          the first filter is stored like this
          <div>
                <p>WHERE</p>

                <div Filter>
                    <Text>
                    <Button>
                </div>
            </div>
           */

        ssql += "All Shares where "+filters[1].lastChild.firstChild.data;

        for (i = 2; i < filters.length-1; i++) {
            /*Remaining filters will be added to the list
            filters are stored like this:
            <div>
                <div Concat> -> filters[i].firstChild
                    <Select> -> filters[i].firstChild.firstChild
                        <Option/>
                        <Option/>
                    </Select>
                </div>

                <div Filter> -> filters[i].lastChild
                    <Text> -> filters[i].lastChild.firstChild
                    <Button>
                </div>
            </div>
            */
            ssql += " " + filters[i].firstChild.firstChild.options[filters[i].firstChild.firstChild.selectedIndex].value;
            ssql += " " + filters[i].lastChild.firstChild.data;
        }
    } else {
        //no filters are given by the user
        ssql = "ALL SHARES";
    }
    $("#query").val(ssql);
    getResults(ssql);
}

/**
 * persist the concatunation state
 * switches the order of the options elements in that state
 * @param concat the select element that changed its state from AND to OR or form OR to AND
 */
function switchConcatState(concat){
    //get the Index of the concat div in the parrent div
    var tmp = concat;
    var  i= 0;
    while((tmp=tmp.previousSibling)!=null) ++i;

    //get the concatunate element out of the parrent
    var ssql = document.getElementById("ssql");
    var conc = ssql.childNodes.item(i).firstChild.firstChild;

    //invert the select options
    conc.innerHTML = concat.firstChild.firstChild.lastChild.outerHTML + concat.firstChild.firstChild.firstChild.outerHTML;


}

/**
 * creates a filter div with an given String and a delete button
 * @param filterString String of the filter that has to be shown in the ssql surch
 * @returns {string} filterDiv with the given String and a button that removes the filterDiv when pressed
 */
function getFilterHTML(filterString) {

    return "<div class= 'filter p-2' >"+filterString+
        "<button type='button' class='close' aria-label='Close' onclick='deleteFilter(this.parentElement.parentElement)'>" +
        "<span aria-hidden='true'>&times</span>" +
        "</button></div>";

}

/**
 * Method called when save button in Modal is pressed
 */
function processValueFilter() {
    var tmp = document.getElementById("operation");
    var operator = tmp.options[tmp.selectedIndex].value;
    var value = document.getElementById("value").value;
    var filterHTML = getFilterHTML("Value " + operator + " " + value);
    renderFilter(filterHTML);
}

/**
 * Modal called by click on (add Filter) Value
 */
function addValueFilter() {
    document.getElementById("filterModal").innerHTML =
        "<div class='modal-header'>" +
        "<h4 class='modal-title'>VALUE</h4>" +
        "<button type='button' class='close' data-dismiss='modal'>&times;</button>" +
        "</div>" +
        "<div class='modal-body d-flex flex-row'>" +
        "<h4>Value</h4>" +
        "<select class='ml-2' id='operation'>" +
        "<option>></option>" +
        "<option><</option>" +
        "<option>=</option>" +
        "</select>" +
        "<input class='ml-2 w-100' id='value' type='number' value='0'>" +
        "</div>" +
        "<div class='modal-footer'>" +
        "<button type='submit' class='btn color-green' data-dismiss='modal' onclick='processValueFilter()'>Save</button>" +
        "</div>";

    $("#modal").modal();

}

/**
 * Method called when save button in Modal is pressed
 */
function processChangeFilter() {
    var tmp = document.getElementById("operation");
    var operator = tmp.options[tmp.selectedIndex].value;
    var days = document.getElementById("days").value;
    var change = document.getElementById("change").value;
    var filterHTML = getFilterHTML("Change since " + days + " days " + operator + " " + change);
    renderFilter(filterHTML);
}

/**
 * Modal called by click on (add Filter) Change
 */
function addChangeFilter() {
    document.getElementById("filterModal").innerHTML =
        "<div class='modal-header'>" +
        "<h4 class='modal-title'>CHANGE</h4>" +
        "<button type='button' class='close' data-dismiss='modal'>&times;</button>" +
        "</div>" +
        "<div class='modal-body d-flex flex-ro'>" +
        "<h5>Change since</h5>" +
        "<input class='ml-2 w-100' id='days' type='number' value='2'>" +
        "<h5>Days</h5>" +
        "<select class='ml-2' id='operation'>" +
        "<option>></option>" +
        "<option><</option>" +
        "<option>=</option>" +
        "</select>" +
        "<input class='ml-2 w-100' id='change' type='number' value='0'>" +
        "</div>" +
        "<div class='modal-footer'>" +
        "<button type='button' class='btn color-green' data-dismiss='modal' onclick='processChangeFilter()'>Save</button>" +
        "</div>";

    $("#modal").modal();
}

/**
*Modal called by click on (add Filter) longest grow
 */
function addLongestGrowFilter() {
    document.getElementById("filterModal").innerHTML =
    "<div class='modal-header'>" +
    "<h4 class='modal-title'>LONGEST GROW</h4>" +
    "<button type='button' class='close' data-dismiss='modal'>&times;</button>" +
    "</div>" +
    "<div class='modal-body d-flex flex-row'>" +
    "<h4>Longest grow</h4>" +
    "<select class='ml-2' id='operation'>" +
    "<option>></option>" +
    "<option><</option>" +
    "<option>=</option>" +
    "</select>" +
    "<input class='ml-2 w-100' id='value' type='number' value='2'>" +
    "</div>" +
    "<div class='modal-footer'>" +
    "<button type='submit' class='btn color-green' data-dismiss='modal' onclick='processLongestGrowFilter()'>Save</button>" +
    "</div>";

    $("#modal").modal();
}

/**
 * Method called when save button in Modal is pressed
 */
function processLongestGrowFilter() {
    var tmp = document.getElementById("operation");
    var operator = tmp.options[tmp.selectedIndex].value;
    var value = document.getElementById("value").value;
    var filterHTML = getFilterHTML("Longest grow " + operator + " " + value );
    renderFilter(filterHTML);
}

/**
 * Modal called by click on (add Filter) Average
 */
function addAverageFilter() {
    document.getElementById("filterModal").innerHTML =
    "<div class='modal-header'>" +
    "<h4 class='modal-title'>Average</h4>" +
    "<button type='button' class='close' data-dismiss='modal'>&times;</button>" +
    "</div>" +
    "<div class='modal-body d-flex flex-row'>" +
    "<h4>Average</h4>" +
    "<select class='ml-2' id='operation'>" +
    "<option>></option>" +
    "<option><</option>" +
    "<option>=</option>" +
    "</select>" +
    "<input class='ml-2 w-100' id='value' type='number' value='2'>" +
    "</div>" +
    "<div class='modal-footer'>" +
    "<button type='submit' class='btn color-green' data-dismiss='modal' onclick='processAverageFilter()'>Save</button>" +
    "</div>";

    $("#modal").modal();
}

/**
 * Method called when save button in Modal is pressed
 */
function processAverageFilter() {
    var tmp = document.getElementById("operation");
    var operator = tmp.options[tmp.selectedIndex].value;
    var value = document.getElementById("value").value;
    var filterHTML = getFilterHTML("Average" + operator + " " + value);
    renderFilter(filterHTML);
}

/**
 * Modal called by click on (add Filter) Variance
 */
function addVarianceFilter() {
    document.getElementById("filterModal").innerHTML =
        "<div class='modal-header'>" +
        "<h4 class='modal-title'>Variance</h4>" +
        "<button type='button' class='close' data-dismiss='modal'>&times;</button>" +
        "</div>" +
        "<div class='modal-body d-flex flex-row'>" +
        "<h4>Variance</h4>" +
        "<select class='ml-2' id='operation'>" +
        "<option>></option>" +
        "<option><</option>" +
        "<option>=</option>" +
        "</select>" +
        "<input class='ml-2 w-100' id='value' type='number' value='2'>" +
        "</div>" +
        "<div class='modal-footer'>" +
        "<button type='submit' class='btn color-green' data-dismiss='modal' onclick='processVarianceFilter()'>Save</button>" +
        "</div>";

    $("#modal").modal();
}

/**
 * Method called when save button in Modal is pressed
 */
function processVarianceFilter() {
    var tmp = document.getElementById("operation");
    var operator = tmp.options[tmp.selectedIndex].value;
    var value = document.getElementById("value").value;
    var filterHTML = getFilterHTML("Variance" + operator + " " + value);
    renderFilter(filterHTML);
}