
Mahesh Menon




from JoinJsons import JoinJson
from ConfigParser import SafeConfigParser
from Logging import logger

def read_conf():
   logger.debug("Reading properties file")

   CONFIG_FILE = "fluxa_properties.conf"
   config = SafeConfigParser()
   config.read(CONFIG_FILE)

   logger.debug("Properties file read")

   return config

if __name__ == '__main__':
   logger.info("Started")
   config = read_conf()

   JoinJson(config).join_jsons()
   logger.info("Completed")
.
.
.
.
.
.
## @package suvoda
########################################################################################################################
# Author: Author Name #
# Version: 1.0 #
# Date created: 05/24/2017 #
# Date last modified: 05/24/2017 #
# Purpose: Posts notification messages to notification server #
########################################################################################################################

#
# Imports all necessary
packages
#

