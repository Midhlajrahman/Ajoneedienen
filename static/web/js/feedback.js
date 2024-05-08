$(document).ready(function () {

    // Check if the modal has been shown before
    var modalShownBefore = sessionStorage.getItem('modalShownBefore');

    if (!modalShownBefore) {
        // Show the modal
        $('#feedbackModal').modal('show');

        // Set the flag in session storage
        sessionStorage.setItem('modalShownBefore', true);
    }

    // Handle form submission using AJAX
    $('#feedbackForm').submit(function (e) {
        e.preventDefault();

        // Set the value of the hidden input field with the selected reaction
        $('#reactionInput').val($('.reaction-btn.active').data('value'));

        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function (response) {
                // Handle success, e.g., show a success message
                alert(response.success);
                // Refresh the page after clicking OK in the alert
                location.reload();
            },
            error: function (error) {
                // Handle errors, e.g., display an error message
                alert('Error: ' + error.responseJSON.error);
            }
        });
    });

    // Handle reaction button clicks
    $('.reaction-btn').click(function () {
        // Remove 'active' class from all buttons
        $('.reaction-btn').removeClass('active');

        // Add 'active' class to the clicked button
        $(this).addClass('active');
    });
});