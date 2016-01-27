$("#likes").click(function () {
    var catid;
    catid = $(this).attr("data-catid");
    $.get('/rango/like_category', {category_id: catid}, function (data) {
        $("#like_count").html(data);
        $("#likes").hide();
    });
});

// When clicked, it will extract the category id from the button element, 
// and then make an AJAX GET request which will make a call to /rango/like_category/ 
// encoding the category_id in the request. If the request is successful, then 
// the HTML element with id like_count (i.e. the <strong> ) is updated with 
// the data returned by the request, and the HTML element with id likes (i.e. the <button>) is hidden.