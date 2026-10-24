module "networking" {
  source      = "./modules/networking"
  project_id  = var.project_id
  region      = var.region
  name_prefix = "${var.name_prefix}-${var.environment}"
  vpc_cidr    = var.vpc_cidr
}

module "gke" {
  source      = "./modules/gke"
  project_id  = var.project_id
  region      = var.region
  name_prefix = "${var.name_prefix}-${var.environment}"
  network     = module.networking.network_id
  subnetwork  = module.networking.subnetwork_id
  node_count  = var.gke_node_count
}

module "cloudsql" {
  source      = "./modules/cloudsql"
  project_id  = var.project_id
  region      = var.region
  name_prefix = "${var.name_prefix}-${var.environment}"
  db_tier     = var.db_tier
}

module "gcr" {
  source      = "./modules/gcr"
  project_id  = var.project_id
  region      = var.region
  name_prefix = "${var.name_prefix}-${var.environment}"
}

module "secret_manager" {
  source      = "./modules/secret-manager"
  project_id  = var.project_id
  name_prefix = "${var.name_prefix}-${var.environment}"
}
