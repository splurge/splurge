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
            $('#recommendations').empty();
            $('#original').empty();
            var imgurl = "http://covers.openlibrary.org/b/ISBN/" + alldata.isbn + "-M.jpg";
            $('#original').append('<div class="cover"><img src="' + imgurl + '" height="200" width="135" alt="" /> <br /> ' + alldata.isbn + '</div>');
                    
	    // Old: just displays the covers in a big long row, all at once
            /* for (i = 0; i < alldata.results.length; i++) {
                var data = alldata.results[i];
                console.log(data);
                //$('#recommendations').append(data);
                var imgurl = "http://covers.openlibrary.org/b/ISBN/" + data[1] + "-M.jpg";
                $('#recommendations').append('<img src="' + imgurl + '" width="75" height="75" alt="" />Rank: <b>' + data[2] + '</b> ISBN:' + data[1] + '<br/>');
            }
	    */

	    var slider;
	    //slider starts here
	    $('#recommendation_slider').empty();
	    if (slider != undefined) {    
		slider.destroyShow();
	    }

	    for (i = 0; i < alldata.results.length; i++) {
                var data = alldata.results[i];
                var imgurl = "http://covers.openlibrary.org/b/ISBN/" + data[1] + "-M.jpg";
                $('#recommendation_slider').append('<div class="cover"><img src="' + imgurl + '" width="135" height="200" alt="" /> <br /> Rank: ' + data[2] + '<br />' + data[1] + '</div>');
                $('#recommendation_slider').resize();
            }
	    
	    //initialize carousel
	    slider = $('#recommendation_slider').bxSlider({
	    	displaySlideQty: 5,
		moveSlideQty: 1,
		infiniteLoop: false
	    });

        });
    });
    $('#isbn').change();
});
