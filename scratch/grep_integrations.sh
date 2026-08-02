#!/bin/bash
for file in $(find backend/app -type f -name "*.py"); do
    grep -Hn -E "upload_report_to_cloudinary|sync_district_to_algolia|send_health_alert_email" $file
done
