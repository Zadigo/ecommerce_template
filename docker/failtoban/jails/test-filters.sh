#!/bin/bash

fail2ban-regex /etc/fail2ban/access.log /etc/fail2ban/filter.d/dana-exploit.conf

# test_dana_exploit() {
#     for $filter in $filters {
#         filter-regex /etc/fail2ban/access.log /etc/fail2ban/
#     }
# }

# test_dana_exploit
