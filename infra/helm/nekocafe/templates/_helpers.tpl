{{- define "nekocafe.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "nekocafe.fullname" -}}
{{- printf "%s" (include "nekocafe.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "nekocafe.labels" -}}
app.kubernetes.io/name: {{ include "nekocafe.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}
