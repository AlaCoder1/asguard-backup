from django.db import models


class ConfigWaf(models.Model):
    rule_engine_initialization = models.CharField(max_length=300, default="On", null=True, blank=True)
    access_request_bodies = models.BooleanField(default=True)
    xml_request_body_parser = models.BooleanField(default=True)
    json_request_body_parser = models.BooleanField(default=True)
    maximum_request_body_size = models.IntegerField(default=13107200, null=True, blank=True)
    request_body_size_files_excluded = models.IntegerField(default=131072, null=True, blank=True)
    request_body_limit_action = models.CharField(max_length=300, default="Reject", null=True, blank=True)
    maximum_parsing_depth_json = models.IntegerField(default=512, null=True, blank=True)
    maximum_number_args_request = models.IntegerField(default=1000, null=True, blank=True)
    pcre_match_limit = models.IntegerField(default=1000, null=True, blank=True)
    pcre_match_limit_recursion = models.IntegerField(default=1000, null=True, blank=True)
    response_body_access = models.BooleanField(default=True)
    response_body_mimetype = models.CharField(max_length=300, default="text/*", null=True, blank=True)
    response_body_limit = models.IntegerField(default=524288, null=True, blank=True)
    response_body_limit_action = models.CharField(max_length=300, default="ProcessPartial", null=True, blank=True)

    class Meta:
        db_table = 'config_waf'
