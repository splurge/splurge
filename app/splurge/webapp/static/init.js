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
            $('#original').empty();
            var imgurl = "http://covers.openlibrary.org/b/ISBN/" + alldata.isbn + "-M.jpg";
            $('#original').append('<div class="cover"><img src="' + imgurl + '" height="100" alt="" /> <br /> ' + alldata.isbn + '</div>');
            // $('#original').append("<h4>Results for: " + alldata.isbn + "</h4><hr/>");
                    
            for (i = 0; i < alldata.results.length; i++) {
                var data = alldata.results[i];
                console.log(data);
                //$('#box').append(data);
                var imgurl = "http://covers.openlibrary.org/b/ISBN/" + data[1] + "-M.jpg";
                $('#box').append('<div class="cover"><img src="' + imgurl + '" height="200" alt="" /> <br /> Rank: ' + data[2] + '<br />' + data[1] + '</div>');
            }
        });
    });
    $('#isbn').change();
});
