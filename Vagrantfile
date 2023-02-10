# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

    # Slave1-Jenkins
      config.vm.box = "ubuntu/focal64"
      config.vm.box_download_insecure=true
      config.vm.hostname = "Docker"
      config.vm.network :forwarded_port, guest: 22, host: 3200, id: 'ssh'
      # Enable provisioning with a shell script. Additional provisioners such as
      # Ansible, Chef, Docker, Puppet and Salt are also available. Please see the
      # documentation for more information about their specific syntax and use.
      config.vm.provision "shell", inline: <<-SHELL
         sudo apt-get update
         echo "--------------------enabled SSH--------------------"
         sudo sed -n 'H;${x;s/\#PasswordAuthentication no/PasswordAuthentication yes/;p;}' /etc/ssh/sshd_config > tmp_sshd_config
         cat tmp_sshd_config > /etc/ssh/sshd_config
         sudo rm tmp_sshd_config
         sudo systemctl restart sshd
         sudo systemctl restart ssh
         #Install docker
          echo "--------------------Installing Docker--------------------"
          sudo apt-get update -y \
              ca-certificates \
              curl \
              gnupg \
              lsb-release
          curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
          echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
          $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
          sudo apt-get update -y
          sudo apt-get install docker-ce docker-ce-cli containerd.io -y
         #Install docker-compose
         echo "--------------------Installing Docker-compose--------------------" 
         sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
         sudo chmod +x /usr/local/bin/docker-compose
         sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
         sudo chmod 666 /var/run/docker.sock
          #Install ansible
          echo "--------------------Installing Ansible--------------------"
          sudo apt update -y
          sudo apt install software-properties-common -y
          sudo add-apt-repository --yes --update ppa:ansible/ansible
          sudo apt install ansible -y
          #Add docker to sudo group
          echo "--------------------Add Docker to Sudo group--------------------"
          sudo groupadd docker && sudo usermod -aG docker $USER && newgrp docker && sudo chmod 777 /var/run/docker.sock
          #Install JDK
          echo "--------------------Install JDK--------------------"
          sudo apt-get update -y
          sudo apt-get install default-jdk -y
          cd /home/vagrant
          mkdir newdms
        
       SHELL
    
    
    end