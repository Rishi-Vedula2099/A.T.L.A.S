locals {
  tags = merge({ Layer = "eks" }, var.tags)
}

# ---------------------------------------------------------------------------
# Cluster
# ---------------------------------------------------------------------------
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.20.0"

  cluster_name    = "${var.name_prefix}-${var.environment}"
  cluster_version = var.kubernetes_version

  vpc_id                   = var.vpc_id
  subnet_ids               = var.subnet_ids
  control_plane_subnet_ids = var.control_plane_subnet_ids

  # Endpoint is private-reachable from inside the VPC, public for kubectl.
  cluster_endpoint_public_access       = true
  cluster_endpoint_public_access_cidrs = ["0.0.0.0/0"] # tighten in prod
  cluster_endpoint_private_access      = true

  # Manage the addons via the module.
  cluster_addons = {
    coredns            = { most_recent = true }
    kube-proxy         = { most_recent = true }
    vpc-cni            = { most_recent = true }
    aws-ebs-csi-driver = { most_recent = true }
  }

  enable_irsa = true

  tags = local.tags
}

# ---------------------------------------------------------------------------
# General-purpose node group
# ---------------------------------------------------------------------------
module "node_group_general" {
  source  = "terraform-aws-modules/eks/aws//modules/eks-managed-node-group"
  version = "~> 20.20.0"

  name            = "general"
  cluster_name    = module.eks.cluster_name
  cluster_version = var.kubernetes_version

  subnet_ids = var.subnet_ids
  vpc_id     = var.vpc_id

  min_size     = var.node_desired_size
  max_size     = var.node_desired_size * 3
  desired_size = var.node_desired_size

  instance_types = [var.node_instance_type]
  capacity_type  = "on-demand"
  disk_size      = 100

  labels = { role = "general" }

  tags = local.tags
}

# ---------------------------------------------------------------------------
# GPU node group (opt-in)
# ---------------------------------------------------------------------------
module "node_group_gpu" {
  source  = "terraform-aws-modules/eks/aws//modules/eks-managed-node-group"
  version = "~> 20.20.0"
  count   = var.enable_gpu ? 1 : 0

  name            = "gpu"
  cluster_name    = module.eks.cluster_name
  cluster_version = var.kubernetes_version

  subnet_ids = var.subnet_ids
  vpc_id     = var.vpc_id

  min_size     = 1
  max_size     = 5
  desired_size = 1

  instance_types = [var.node_gpu_instance_type]
  capacity_type  = "on-demand"
  disk_size      = 200

  # GPU nodes need the NVIDIA device plugin — install via Helm after the cluster is up.
  labels = { role = "gpu", "nvidia.com/gpu" = "present" }
  taints = [{
    key    = "nvidia.com/gpu"
    value  = "present"
    effect = "NO_SCHEDULE"
  }]

  tags = local.tags
}

# ---------------------------------------------------------------------------
# Storage class for the in-cluster volumes (used by Helm chart).
# ---------------------------------------------------------------------------
resource "kubernetes_storage_class" "gp3" {
  count = 0 # opt-in: requires kubectl/k8s provider configured post-apply.

  metadata {
    name = "gp3"
    annotations = {
      "storageclass.kubernetes.io/is-default-class" = "true"
    }
  }

  storage_provisioner = "ebs.csi.aws.com"
  volume_binding_mode = "WaitForFirstConsumer"
  parameters = {
    type      = "gp3"
    fsType    = "ext4"
    encrypted = "true"
  }
}
