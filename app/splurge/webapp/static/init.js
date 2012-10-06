$(function() {
    
    $.getJSON('../splurge_service_getinstitutions/', function(data) {
        console.log(institution_list);
        $('#institution_list').empty();
        $('#institution_list').append('any');
        for (i = 0; i < data.institutions.length; i++) {
            $('#institution_list').append(', ' + data.institutions[i][1] )
        }
    });
    
    $('#go').click( function() {
        var url = '../splurge_service/' + $('#isbn').val() + '/' + $('#institutions').val() + '/' + $('#startDate').val() + '/'+ $('#endDate').val() + '/';
        $.getJSON(url, function(alldata) {
            console.log(alldata);
            $('#box').empty();
            var imgurl = "http://covers.openlibrary.org/b/ISBN/" + alldata.isbn + "-M.jpg";
            $('#box').append('<img src="' + imgurl + '" height="75" alt="" /><br/>');
            $('#box').append("<h4>Results for: " + alldata.isbn + "</h4><hr/>");
                    
            for (i = 0; i < alldata.results.length; i++) {
                var data = alldata.results[i];
                console.log(data);
                //$('#box').append(data);
                var imgurl = "http://covers.openlibrary.org/b/ISBN/" + data[1] + "-M.jpg";
                $('#box').append('<img src="' + imgurl + '" height="75" alt="" />Rank: <b>' + data[2] + '</b> ISBN:' + data[1] + '<br/>');
            }
        });
    });
    $('#isbn').change();
});
