from flask_admin.contrib.fileadmin import FileAdmin
from flask_login import current_user


class CustomFileAdmin(FileAdmin):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()
