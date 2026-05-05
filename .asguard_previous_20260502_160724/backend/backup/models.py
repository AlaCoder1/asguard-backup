from django.db import models


class CloudStorageConfig(models.Model):
    PROVIDER_CHOICES = [
        ("backblaze_b2",   "Backblaze B2"),
        ("cloudflare_r2",  "Cloudflare R2"),
        ("aws_s3",         "AWS S3"),
        ("minio",          "MinIO (self-hosted)"),
        ("custom",         "Custom S3-compatible"),
    ]

    provider        = models.CharField(max_length=30, choices=PROVIDER_CHOICES, default="backblaze_b2")
    endpoint_url    = models.CharField(max_length=255, blank=True, help_text="Leave empty for AWS S3")
    access_key_id   = models.CharField(max_length=255)
    secret_access_key = models.CharField(max_length=255)   # stored encrypted via Django-fernet or raw
    bucket_name     = models.CharField(max_length=255)
    region          = models.CharField(max_length=50, default="us-east-1")
    prefix          = models.CharField(max_length=255, default="asguard-backups/",
                                       help_text="Folder prefix inside bucket")
    enabled         = models.BooleanField(default=True)
    auto_upload     = models.BooleanField(default=True,
                                          help_text="Auto-upload after every backup")
    upload_db_only_to_cloud = models.BooleanField(default=False,
                                                   help_text="DB backups go to cloud only, not kept locally")
    max_cloud_copies = models.PositiveIntegerField(default=10,
                                                    help_text="Max backups to keep in cloud (oldest deleted)")
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "backup_cloud_config"

    def __str__(self):
        return f"{self.get_provider_display()} — {self.bucket_name}"


class BackupRecord(models.Model):
    STATUS_CHOICES = [
        ("ok",      "Success"),
        ("partial", "Partial"),
        ("error",   "Error"),
    ]
    TYPE_CHOICES = [
        ("safe_backup", "Safe Backup"),
        ("full_backup", "Full Backup"),
        ("db_backup",   "DB Backup"),
        ("custom",      "Custom Backup"),
    ]

    backup_id           = models.CharField(max_length=100, unique=True)
    backup_type         = models.CharField(max_length=20, choices=TYPE_CHOICES)
    backup_scope        = models.CharField(max_length=100, blank=True)
    created_at          = models.DateTimeField()
    status              = models.CharField(max_length=10, choices=STATUS_CHOICES)
    health_score        = models.IntegerField(null=True, blank=True)
    size_mb             = models.FloatField(null=True, blank=True)
    components_success  = models.IntegerField(default=0)
    components_failed   = models.IntegerField(default=0)
    components_skipped  = models.IntegerField(default=0)
    message             = models.TextField(blank=True)
    local_path          = models.CharField(max_length=500, blank=True)
    # Cloud sync fields
    cloud_uploaded      = models.BooleanField(default=False)
    cloud_provider      = models.CharField(max_length=30, blank=True)
    cloud_bucket        = models.CharField(max_length=255, blank=True)
    cloud_key           = models.CharField(max_length=500, blank=True,
                                           help_text="S3 object key in bucket")
    cloud_size_mb       = models.FloatField(null=True, blank=True)
    cloud_uploaded_at   = models.DateTimeField(null=True, blank=True)
    cloud_error         = models.TextField(blank=True)

    class Meta:
        db_table  = "backup_record"
        ordering  = ["-created_at"]

    def __str__(self):
        return f"{self.backup_id} [{self.status}]"

    def to_dict(self):
        return {
            "id":                  self.pk,
            "backup_id":           self.backup_id,
            "backup_type":         self.backup_type,
            "backup_scope":        self.backup_scope,
            "created_at":          self.created_at.isoformat() if self.created_at else None,
            "status":              self.status,
            "health_score":        self.health_score,
            "size_mb":             self.size_mb,
            "components_success":  self.components_success,
            "components_failed":   self.components_failed,
            "components_skipped":  self.components_skipped,
            "message":             self.message,
            "local_path":          self.local_path,
            "cloud_uploaded":      self.cloud_uploaded,
            "cloud_provider":      self.cloud_provider,
            "cloud_bucket":        self.cloud_bucket,
            "cloud_key":           self.cloud_key,
            "cloud_size_mb":       self.cloud_size_mb,
            "cloud_uploaded_at":   self.cloud_uploaded_at.isoformat() if self.cloud_uploaded_at else None,
            "cloud_error":         self.cloud_error,
        }
