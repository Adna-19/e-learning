from django.core.management import call_command

def create_scheduled_backups():
  try:
    call_command('dbbackup')
  except:
    pass