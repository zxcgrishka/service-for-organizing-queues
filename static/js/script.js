document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('registerButton').addEventListener('click', function() {
        window.location.href = 'register';
    });

    document.getElementById('loginButton').addEventListener('click', function() {
        window.location.href = 'login';
    });
});
