#!/bin/bash
# View logs for Aura services
# Usage: ./logs.sh <service> <environment> [namespace]
# Example: ./logs.sh backend dev aura-dev

set -e

SERVICE="${1}"
ENVIRONMENT="${2:-dev}"
NAMESPACE="${3:-aura-${ENVIRONMENT}}"

if [ -z "$SERVICE" ]; then
    echo "Usage: $0 <service> [environment] [namespace]"
    echo "Services: backend, web-dashboard, postgres, migrations"
    exit 1
fi

case "$SERVICE" in
    backend)
        kubectl logs -n "${NAMESPACE}" -l app=backend --tail=100 -f
        ;;
    web-dashboard|web)
        kubectl logs -n "${NAMESPACE}" -l app=web-dashboard --tail=100 -f
        ;;
    postgres|db)
        kubectl logs -n "${NAMESPACE}" -l app=postgres --tail=100 -f
        ;;
    migrations|migration)
        kubectl logs -n "${NAMESPACE}" -l app=migrations --tail=100 -f
        ;;
    *)
        echo "Unknown service: $SERVICE"
        echo "Available services: backend, web-dashboard, postgres, migrations"
        exit 1
        ;;
esac
