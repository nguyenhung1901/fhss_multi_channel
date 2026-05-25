#!/bin/bash
#
#  This script will be run after parameterization has completed, e.g., 
#  use this to compile source code that has been parameterized.
#  The container user password will be passed as the first argument,
#  (the user ID is the second parameter)
#  If this script is to use sudo and the sudoers for the lab
#  does not permit nopassword, then use:
#  echo $1 | sudo -S the-command
#
#  If you issue commands herein to start services, and those services
#  have unit files prescribing their being started after the
#  waitparam.service, then first create the flag directory that
#  waitparam sleeps on:
#
#   PERMLOCKDIR=/var/labtainer/did_param
#   echo $1 | sudo -S mkdir -p "$PERMLOCKDIR"


# Patch Labtainer bash-pre-capinout unsafe tests.
# Without quotes, empty array elements can cause:
# [: ==: unary operator expected
cap="$HOME/.local/bin/bash-pre-capinout.sh"
if [ -f "$cap" ]; then
    sed -i 's/\[ ${orig_cmd_array\[0\]} == "sudo" \]/[ "${orig_cmd_array[0]}" = "sudo" ]/g' "$cap"
    sed -i 's/\[ ${cmd_line_array\[0\]} == "sudo" \]/[ "${cmd_line_array[0]}" = "sudo" ]/g' "$cap"
    sed -i 's/\[ ${cmd_line_array\[0\]} == "time" \]/[ "${cmd_line_array[0]}" = "time" ]/g' "$cap"
    sed -i 's/\[ ${cmd_line_array\[0\]} == "sh" \]/[ "${cmd_line_array[0]}" = "sh" ]/g' "$cap"
    sed -i 's/\[ ${cmd_line_array\[0\]} == "bash" \]/[ "${cmd_line_array[0]}" = "bash" ]/g' "$cap"
    sed -i 's/\[ $result == 1 \]/[ "$result" = "1" ]/g' "$cap"
fi
