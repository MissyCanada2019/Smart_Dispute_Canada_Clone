<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}SmartDispute Canada{% endblock %}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Optional Custom Theme -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/canada-theme.css') }}">
    
    <!-- Favicon -->
    <link rel="icon" href="{{ url_for('static', filename='logo.png') }}" type="image/png">
</head>
<body>

<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #b71c1c;">
    <div class="container-fluid">
        <a class="navbar-brand" href="{{ url_for('routes.home') }}">
            <img src="{{ url_for('static', filename='logo.png') }}" alt="SmartDispute Logo" width="40" height="40" class="d-inline-block align-text-top">
            SmartDispute Canada
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                data-bs-target="#navbarNav" aria-controls="navbarNav"
                aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
            <ul class="navbar-nav">
                {% if current_user.is_authenticated %}
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('routes.dashboard') }}">Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('routes.upload') }}">Upload</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('routes.logout') }}">Logout</a></li>
                {% else %}
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('routes.login') }}">Login</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('routes.register') }}">Register</a></li>
                {% endif %}
            </ul>
        </div>
    </div>
</nav>

<!-- Page Content -->
<main class="container-fluid px-0">
    {% block content %}{% endblock %}
</main>

<!-- Footer -->
<footer class="text-center py-4 mt-5" style="background-color: #d32f2f; color: white;">
    <div>
        Proudly Canadian | SmartDispute.ai © {{ now().year }}
    </div>
</footer>

<!-- Bootstrap JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>