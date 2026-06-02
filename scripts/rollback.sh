#!/usr/bin/env sh
set -eu

ENVIRONMENT="${1:-staging}"
RELEASE="${2:-nekocafe}"
NAMESPACE="nekocafe-${ENVIRONMENT}"

echo "Rollback release ${RELEASE} in namespace ${NAMESPACE}"
echo "helm history ${RELEASE} -n ${NAMESPACE}"
echo "helm rollback ${RELEASE} 0 -n ${NAMESPACE}"
echo "kubectl rollout status deploy/${RELEASE}-reservation-service -n ${NAMESPACE} --timeout=120s"
echo "kubectl rollout status deploy/${RELEASE}-member-service -n ${NAMESPACE} --timeout=120s"
