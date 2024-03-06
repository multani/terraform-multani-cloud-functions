#!/usr/bin/env python3

from multani import functions
from multani import logging
from multani import tracing

logging.configure()
tracing.global_setup()

error_reporting_slack = functions.error_reporting_slack
terraform_cloud_trigger_all = functions.terraform_cloud_trigger_all
