module.exports = {
  apps: [
    {
      name: 'thequicksnapapp',
      script: 'poetry',
      args: 'run python manage.py runserver 0.0.0.0:8101',
      interpreter: 'bash',
      env: {
        PYTHONUNBUFFERED: "1",
        DJANGO_SETTINGS_MODULE: "shiv_shakti.settings",
        // add other environment variables here if needed
      }
    }
  ]
};
