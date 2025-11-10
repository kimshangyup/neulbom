from django.db import models


class VisitorLog(models.Model):
    """
    Track visitor analytics for the public landing page.
    Used to calculate daily, weekly, and monthly visitor counts.
    """
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    path = models.CharField(max_length=255)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Visitor Log'
        verbose_name_plural = 'Visitor Logs'

    def __str__(self):
        return f"{self.ip_address} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
