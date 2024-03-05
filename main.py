#!/usr/bin/env python3

from multani import functions
from multani import logging
from multani import tracing

logging.configure()
tracing.global_setup()

error_reporting_slack = functions.error_reporting_slack
trigger_all_handler = functions.trigger_all_handler
trigger_single_handler = functions.trigger_single_handler
