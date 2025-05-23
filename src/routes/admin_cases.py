<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Admin Dashboard | SmartDispute.ai</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Admin Dashboard</h2>
      {% if current_user.is_authenticated %}
        <form method="GET" action="{{ url_for('auth.logout') }}">
          <button type="submit" class="btn btn-outline-danger btn-sm">Logout</button>
        </form>
      {% endif %}
    </div>

    <!-- Admin tools, user filters, case lists go here -->

  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
