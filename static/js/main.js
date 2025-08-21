// Main JavaScript file for Goal Line Report

$(document).ready(function() {
    console.log('Goal Line Report - Application loaded');
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(event) {
        var target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 70
            }, 1000);
        }
    });
    
    // Add loading animation to buttons
    $('.btn').on('click', function() {
        var $btn = $(this);
        var originalText = $btn.text();
        
        // Only add loading state if it's not already loading
        if (!$btn.hasClass('loading')) {
            $btn.addClass('loading').text('Loading...');
            
            // Reset after 2 seconds (for demo purposes)
            setTimeout(function() {
                $btn.removeClass('loading').text(originalText);
            }, 2000);
        }
    });
    
    // Card hover effects
    $('.card').hover(
        function() {
            $(this).addClass('shadow-lg');
        },
        function() {
            $(this).removeClass('shadow-lg');
        }
    );
    
    // Form validation example
    $('form').on('submit', function(e) {
        var requiredFields = $(this).find('[required]');
        var isValid = true;
        
        requiredFields.each(function() {
            if (!$(this).val()) {
                $(this).addClass('is-invalid');
                isValid = false;
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            showNotification('Please fill in all required fields.', 'error');
        }
    });
    
    // Notification function
    function showNotification(message, type) {
        var alertClass = type === 'error' ? 'alert-danger' : 'alert-success';
        var notification = $('<div class="alert ' + alertClass + ' alert-dismissible fade show" role="alert">' +
            message +
            '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
            '</div>');
        
        $('.container').prepend(notification);
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            notification.fadeOut('slow');
        }, 5000);
    }
    
    // Example AJAX call (for future use)
    function makeAjaxCall(url, data, successCallback) {
        $.ajax({
            url: url,
            method: 'POST',
            data: data,
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (successCallback) {
                    successCallback(response);
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX Error:', error);
                showNotification('An error occurred. Please try again.', 'error');
            }
        });
    }
    
    // Make functions globally available
    window.goalLineReport = {
        showNotification: showNotification,
        makeAjaxCall: makeAjaxCall
    };
});
