{{/*
Common labels applied to every resource.
*/}}
{{- define "atlas.labels" -}}
app.kubernetes.io/name: atlas
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{/*
Selector labels — narrower than common labels so they're stable for matching.
*/}}
{{- define "atlas.selectorLabels" -}}
app.kubernetes.io/name: atlas
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Component-prefixed labels for individual services.
Usage: {{ include "atlas.componentLabels" (list $.Values.backend "backend") }}
*/}}
{{- define "atlas.componentLabels" -}}
{{- $component := index . 1 -}}
{{- $cfg := index . 0 -}}
app.kubernetes.io/component: {{ $component }}
{{- end -}}

{{/*
Resolve a fully-qualified image reference.
*/}}
{{- define "atlas.image" -}}
{{- $repo := required "repository is required" .repository -}}
{{- $root := required "root context is required" .root -}}
{{- printf "%s/%s:%s" $root.Values.image.registry $repo $root.Values.image.tag -}}
{{- end -}}

{{/*
Build the image pullSecrets block, or empty.
*/}}
{{- define "atlas.imagePullSecrets" -}}
{{- with .Values.image.pullSecrets }}
imagePullSecrets:
{{- toYaml . | nindent 2 }}
{{- end }}
{{- end -}}
