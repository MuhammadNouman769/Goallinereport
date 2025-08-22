from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html

# Unregister the default Group model
admin.site.unregister(Group)

# Customize the admin site
admin.site.site_header = "Goal Line Report Administration"
admin.site.site_title = "Goal Line Report Admin"
admin.site.index_title = "Welcome to Goal Line Report Administration"

# Custom admin site class
class GoalLineReportAdminSite(admin.AdminSite):
    site_header = "Goal Line Report Administration"
    site_title = "Goal Line Report Admin"
    index_title = "Welcome to Goal Line Report Administration"
    
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)
        
        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        
        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])
        
        return app_list

# Create custom admin site instance
admin_site = GoalLineReportAdminSite(name='goallinereport_admin')
