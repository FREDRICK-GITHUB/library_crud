
$(function () {
    $("#date").datepicker({
        dateFormat: "dd-mm-yy" 
    });
});
$(document).ready(function () {
    $('#searchButton').click(function () {
        var query = $('#searchInput').val();
        $.getJSON('/search?q=' + query, function (data) {
            var resultsHtml = '';
            data.forEach(function (book_record) {
                resultsHtml += '<div class="card mb-3">';
                resultsHtml += '<div class="card-body">';
                resultsHtml += '<h5 class="card-title">' + book_record.title + '</h5>';
                resultsHtml += '<p class="card-text">Author(s): ' + book_record.authors + '</p>';
                resultsHtml += '<p class="card-text">Genre: ' + book_record.genre + '</p>';
                resultsHtml += '<p class="card-text">Quantity: ' + book_record.quantity + '</p>';
                resultsHtml += '<p class="card-text">Borrowed: ' + book_record.borrowed + '</p>';
                resultsHtml += '<p class="card-text">Borrowed and Returned: ' + book_record.borrowed_returned + '</p>';
                resultsHtml += '<p class="card-text">Charge Fee: ' + book_record.charge_fee + '</p>';
                resultsHtml += '</div>';
                resultsHtml += '</div>'; 
            });
            $('#searchResults').html(resultsHtml);
        });
    });
});
