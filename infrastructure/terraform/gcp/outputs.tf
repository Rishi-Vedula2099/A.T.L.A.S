output "gke_cluster_name" {
  value = module.gke.cluster_name
}

output "gke_endpoint" {
  value = module.gke.endpoint
}

output "cloudsql_connection_name" {
  value = module.cloudsql.connection_name
}

output "artifact_registry_url" {
  value = module.gcr.repository_url
}
