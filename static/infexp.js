String.prototype.capitalize = function(){
    return this.replace(/\S+/g, function(a){
        return a.charAt(0).toUpperCase() + a.slice(1).toLowerCase();
    });
};

var personClicked = function(e) {
    window.personOverlay.load();
    $("#personName").html(e.target.innerHTML);
    var person_id = e.target.innerHTML.toLowerCase().replace(" ", "_");
    $.getJSON("/person/"+person_id, function(json) {
        
        if(json.url !== "") {
            $("#memberOf").html("Member of <a href='" + json.url + "'>" + json.name + "</a>.");
        }
        
        $("#homepageUrl").html("Homepage: <a href='" + json.homepage_url + "'>"+json.homepage_url+"</a>");

        $("#personPhoto").attr("src", json.photo_url);
        
        var html = "";
        $.each(json.keywords, function(i) {
            html += json.keywords[i] + ",&nbsp;&nbsp;"
        });
        html = html.substring(0, html.length - 13);
        $("#personKeywords").html(html);
    });
    
}


var wordClicked = function(e) {
    $("#clearQueryButton").show();
    var oldQuery = $("#queryWords").val();
    if(oldQuery == "") {
        $("#queryWords").val(e.target.innerHTML);
        $("#queryDisplay").html(e.target.innerHTML);
    } else {
        $("#queryWords").val(oldQuery + ", " + e.target.innerHTML);
        $("#queryDisplay").html($("#queryDisplay").html() + "&nbsp;<span style='color: #3c3;'>&rarr;</span>&nbsp;" + e.target.innerHTML);
    }
    
    $("#spinner").toggle();
    var data = {"queryWords": $("#queryWords").val(),
                "peopleCount": $("#people > ul li").length
               };
    $.post("/query", data, function(json) {
        html = wordCloudHtml(json.weights);
        $("#wordCloud").html(html);

        html = "<ul>";
        $.each(json.people, function(i, person_name) {
            capitalized_name = "";
            $.each(person_name.split("_"), function(i, comp) {
                capitalized_name += comp.capitalize() + " ";
            });
            html += "<li><a href='#962' class='dkt'>" + capitalized_name + "</a></li>";
        });
        html += "</ul>";

        $("#mp").html("matching people ("+ json.people.length +")");

        $("#people").html(html);
        $("#spinner").toggle();
        
        $("#wordCloud > a").bind("click", function(e) { wordClicked(e); });
        $("#people > ul > li > a").bind("click", function(e) { personClicked(e); });
        
    }, "json");
    
}

var loadInitialData = function() {
    $.getJSON("/init_json", function(json) {
        html = wordCloudHtml(json);
        $("#wordCloud").html(html);
        $("a").bind("click", function(e) { wordClicked(e); });
    });
}

var wordCloudHtml = function(weightsJson) {
    html = "";
    var i = 0;
    $.each(weightsJson, function(word, weight) {
        if(i % 2 == 0) {
            html += "<a href='#' class='w" + weight + " zebra1'>" + word + "</a> ";
        } else {
            html += "<a href='#' class='w" + weight + " zebra2'>" + word + "</a> ";
        }
        i++;
    });
    return html;
}