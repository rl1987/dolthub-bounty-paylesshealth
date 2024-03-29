terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = file("do_token.txt")
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
  size      = "s-1vcpu-1gb"
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

