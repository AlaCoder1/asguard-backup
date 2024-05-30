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


class RulesWaf(models.Model):
    name = models.CharField(max_length=300, default=None, null=True, blank=True, unique=True)
    rule_status = models.BooleanField(default=True)
    created = models.BooleanField(default=True)
    rule_id = models.IntegerField(default=None, null=True, unique=True)
    variables = models.CharField(max_length=1000, default=None, null=True, blank=True)
    operators = models.CharField(max_length=1000, default=None, null=True, blank=True)
    transformations = models.CharField(max_length=1000, default=None, null=True, blank=True)
    actions = models.CharField(max_length=1000, default=None, null=True, blank=True)
    rule_content = models.CharField(max_length=3000, default=None, null=True, blank=True)

    class Meta:
        db_table = 'rules_waf'


class ApplicationWaf(models.Model):
    name = models.CharField(max_length=300, default=None, null=True, blank=True, unique=True)
    application_type = models.CharField(max_length=100, default="ip", null=True, blank=True)
    application_value = models.CharField(max_length=100, default=None, null=True, blank=True)
    description = models.CharField(max_length=1000, default=None, null=True, blank=True)
    rules = models.ManyToManyField(RulesWaf, through="ApplicationRulesWaf")

    class Meta:
        db_table = 'application_waf'


class ApplicationRulesWaf(models.Model):
    application_waf = models.ForeignKey(ApplicationWaf, on_delete=models.CASCADE)
    rule_waf = models.ForeignKey(RulesWaf, on_delete=models.CASCADE)
    rule_policy = models.BooleanField(default=False)
    rule_log = models.BooleanField(default=False)

    class Meta:
        db_table = 'application_rule_waf'
