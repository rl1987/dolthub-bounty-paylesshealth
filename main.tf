terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = "1c6508e264c30fcc6249f937d2d4eb2cacd6ebbf25b1b7cd300b777cb2339195"
}

data "digitalocean_ssh_keys" "keys" {
  sort {
    key       = "name"
    direction = "asc"
  }
}

resource "digitalocean_droplet" "server" {
  image     = "debian-11-x64"
  name      = "dhdb-paylesshealth"
  region    = "sfo3"
  size      = "s-1vcpu-2gb"
  ssh_keys  = [ for key in data.digitalocean_ssh_keys.keys.ssh_keys: key.fingerprint ]
  user_data = file("provision.sh")

  connection {
    host        = self.ipv4_address
    user        = "root"
    type        = "ssh"
    timeout     = "2m"
    private_key = file("~/.ssh/id_ed25519")
  }

  provisioner "file" {
    source      = "~/.dolt"
    destination = "/root"
  }
}

output "server_ip" {
  value = resource.digitalocean_droplet.server.ipv4_address
}

