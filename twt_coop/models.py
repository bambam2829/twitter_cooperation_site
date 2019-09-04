from django.db import models


class OAuthTokenTemp(models.Model):
    user_id = models.CharField(max_length=30, db_index=True, null=True)
    oauth_token = models.CharField(max_length=255, db_index=True, unique=True)
    oauth_token_secret = models.CharField(
        max_length=255, db_index=True, unique=True)
